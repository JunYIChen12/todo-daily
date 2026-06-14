const STORAGE_KEY = "daily-todos-v2";
const LEGACY_STORAGE_KEY = "daily-todos-v1";
const SERVER_STORE_URL = "/api/store";
const SERVER_STATUS_URL = "/api/status";
const SERVER_TEST_NOTIFICATION_URL = "/api/test-notification";

const state = {
  store: loadStore(),
  selectedDate: toDateKey(new Date()),
  filter: "all",
  search: "",
  notified: new Set(),
  backgroundAvailable: false,
  saveTimer: null,
  noteTimers: new Map(),
};

const elements = {
  dateInput: document.querySelector("#dateInput"),
  prevDay: document.querySelector("#prevDay"),
  nextDay: document.querySelector("#nextDay"),
  todayBtn: document.querySelector("#todayBtn"),
  totalCount: document.querySelector("#totalCount"),
  openCount: document.querySelector("#openCount"),
  doneCount: document.querySelector("#doneCount"),
  progressText: document.querySelector("#progressText"),
  progressBar: document.querySelector("#progressBar"),
  dateLabel: document.querySelector("#dateLabel"),
  searchInput: document.querySelector("#searchInput"),
  todoForm: document.querySelector("#todoForm"),
  titleInput: document.querySelector("#titleInput"),
  timeInput: document.querySelector("#timeInput"),
  priorityInput: document.querySelector("#priorityInput"),
  tagInput: document.querySelector("#tagInput"),
  remindInput: document.querySelector("#remindInput"),
  repeatInput: document.querySelector("#repeatInput"),
  todoList: document.querySelector("#todoList"),
  emptyTemplate: document.querySelector("#emptyTemplate"),
  notificationStatus: document.querySelector("#notificationStatus"),
  enableNotificationsBtn: document.querySelector("#enableNotificationsBtn"),
  testNotificationBtn: document.querySelector("#testNotificationBtn"),
  filters: Array.from(document.querySelectorAll(".filter")),
  toast: document.querySelector("#toast"),
};

function loadStore() {
  const empty = { days: {}, recurring: [] };
  try {
    const current = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (current && current.days && Array.isArray(current.recurring)) return current;

    const legacy = JSON.parse(localStorage.getItem(LEGACY_STORAGE_KEY));
    if (legacy && typeof legacy === "object") return { days: legacy, recurring: [] };
  } catch {
    return empty;
  }
  return empty;
}

function saveStore() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.store));
  scheduleServerSave();
}

async function loadServerStore() {
  try {
    const response = await fetch(SERVER_STORE_URL, { cache: "no-store" });
    if (!response.ok) throw new Error("Store unavailable");
    const serverStore = await response.json();
    state.backgroundAvailable = true;

    if (hasTodos(serverStore)) {
      state.store = normalizeStore(serverStore);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.store));
    } else if (hasTodos(state.store)) {
      await saveStoreToServer();
    }
  } catch {
    state.backgroundAvailable = false;
  }

  render();
}

function normalizeStore(store) {
  if (store && store.days && Array.isArray(store.recurring)) return store;
  if (store && typeof store === "object" && !Array.isArray(store)) return { days: store, recurring: [] };
  return { days: {}, recurring: [] };
}

function hasTodos(store) {
  const normalized = normalizeStore(store);
  return Object.values(normalized.days).some((todos) => Array.isArray(todos) && todos.length) || normalized.recurring.length > 0;
}

function scheduleServerSave() {
  window.clearTimeout(state.saveTimer);
  state.saveTimer = window.setTimeout(saveStoreToServer, 250);
}

async function saveStoreToServer() {
  const wasAvailable = state.backgroundAvailable;
  try {
    const response = await fetch(SERVER_STORE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state.store),
    });
    state.backgroundAvailable = response.ok;
    if (response.status === 409) {
      await loadServerStore();
      return;
    }
  } catch {
    state.backgroundAvailable = false;
  }
  if (state.backgroundAvailable !== wasAvailable) renderNotificationStatus();
}

function toDateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function fromDateKey(dateKey) {
  const [year, month, day] = dateKey.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function getDayTodos(dateKey = state.selectedDate) {
  const normalTodos = (state.store.days[dateKey] || []).map((todo) => ({ ...todo, source: "single" }));
  const recurringTodos = state.store.recurring
    .filter((todo) => isRecurringActiveOnDate(todo, dateKey))
    .map((todo) => {
      const dayState = todo.dayState?.[dateKey] || {};
      return { ...todo, ...dayState, source: "recurring", instanceDate: dateKey };
    });

  return [...normalTodos, ...recurringTodos].sort(compareTodos);
}

function isRecurringActiveOnDate(todo, dateKey) {
  return todo.startDate <= dateKey && (!todo.endDate || dateKey < todo.endDate) && !todo.deletedDates?.includes(dateKey);
}

function compareTodos(a, b) {
  if (a.done !== b.done) return Number(a.done) - Number(b.done);
  if (a.time && b.time) return a.time.localeCompare(b.time);
  if (a.time) return -1;
  if (b.time) return 1;
  return new Date(a.createdAt) - new Date(b.createdAt);
}

function setDayTodos(todos, dateKey = state.selectedDate) {
  state.store.days[dateKey] = todos;
  saveStore();
}

function addTodo({ title, time, priority, tag, remind, repeatDaily }) {
  const todo = {
    id: crypto.randomUUID(),
    title,
    time,
    priority,
    tag,
    note: "",
    remind,
    done: false,
    createdAt: new Date().toISOString(),
  };

  if (repeatDaily) {
    state.store.recurring.push({ ...todo, startDate: state.selectedDate, dayState: {} });
    saveStore();
    return;
  }

  setDayTodos([todo, ...(state.store.days[state.selectedDate] || [])]);
}

function updateTodo(todo, patch) {
  if (todo.source === "recurring") {
    const target = state.store.recurring.find((item) => item.id === todo.id);
    if (!target) return;
    target.dayState = target.dayState || {};
    target.dayState[state.selectedDate] = { ...(target.dayState[state.selectedDate] || {}), ...patch };
    saveStore();
    return;
  }

  setDayTodos((state.store.days[state.selectedDate] || []).map((item) => (item.id === todo.id ? { ...item, ...patch } : item)));
}

function deleteTodo(todo) {
  if (todo.source === "recurring") {
    const target = state.store.recurring.find((item) => item.id === todo.id);
    if (!target) return;
    const deleteAll = confirm("这是每天重复的待办。确定要从所有日期删除吗？点击“取消”则只删除今天。");
    if (deleteAll) {
      state.store.recurring = state.store.recurring.filter((item) => item.id !== todo.id);
    } else {
      target.deletedDates = Array.from(new Set([...(target.deletedDates || []), state.selectedDate]));
    }
    saveStore();
    return;
  }

  setDayTodos((state.store.days[state.selectedDate] || []).filter((item) => item.id !== todo.id));
}

function stopRecurringTodo(todo) {
  const target = state.store.recurring.find((item) => item.id === todo.id);
  if (!target) return;

  const confirmed = confirm("确定从今天起终止这个每天重复的待办吗？之前日期的记录会保留。");
  if (!confirmed) return;

  target.endDate = state.selectedDate;
  saveStore();
}

function filteredTodos() {
  const needle = state.search.trim().toLowerCase();
  return getDayTodos().filter((todo) => {
    const matchesFilter =
      state.filter === "all" ||
      (state.filter === "open" && !todo.done) ||
      (state.filter === "done" && todo.done) ||
      (state.filter === "high" && todo.priority === "high") ||
      (state.filter === "repeat" && todo.source === "recurring");

    const haystack = `${todo.title} ${todo.tag} ${todo.note} ${todo.time}`.toLowerCase();
    return matchesFilter && (!needle || haystack.includes(needle));
  });
}

function priorityLabel(priority) {
  return { high: "重要", normal: "普通", low: "稍后" }[priority] || "普通";
}

function render() {
  const todos = getDayTodos();
  const doneCount = todos.filter((todo) => todo.done).length;
  const openCount = todos.length - doneCount;
  const progress = todos.length ? Math.round((doneCount / todos.length) * 100) : 0;

  elements.dateInput.value = state.selectedDate;
  elements.totalCount.textContent = todos.length;
  elements.openCount.textContent = openCount;
  elements.doneCount.textContent = doneCount;
  elements.progressText.textContent = `${progress}%`;
  elements.progressBar.style.width = `${progress}%`;
  elements.dateLabel.textContent = formatDateLabel(state.selectedDate);

  elements.filters.forEach((button) => {
    button.classList.toggle("active", button.dataset.filter === state.filter);
  });

  renderNotificationStatus();
  renderList(filteredTodos());
}

function renderList(todos) {
  elements.todoList.replaceChildren();

  if (!todos.length) {
    elements.todoList.append(elements.emptyTemplate.content.cloneNode(true));
    return;
  }

  todos.forEach((todo) => {
    const item = document.createElement("li");
    item.className = `todo-item${todo.done ? " done" : ""}${isDueSoon(todo) ? " due" : ""}`;

    const checkButton = document.createElement("button");
    checkButton.type = "button";
    checkButton.className = `check-btn${todo.done ? " is-done" : ""}`;
    checkButton.textContent = todo.done ? "✓" : "";
    checkButton.title = todo.done ? "标记为未完成" : "标记为完成";
    checkButton.addEventListener("click", () => {
      updateTodo(todo, { done: !todo.done });
      render();
    });

    const main = document.createElement("div");
    main.className = "todo-main";

    const titleRow = document.createElement("div");
    titleRow.className = "todo-title-row";

    const title = document.createElement("span");
    title.className = "todo-title";
    title.textContent = todo.title;

    const time = document.createElement("span");
    time.className = "time-pill";
    time.textContent = todo.time ? todo.time : "未设时间";

    const badge = document.createElement("span");
    badge.className = `badge ${todo.priority}`;
    badge.textContent = priorityLabel(todo.priority);

    titleRow.append(time, title, badge);

    if (todo.source === "recurring") {
      const repeat = document.createElement("span");
      repeat.className = "repeat-pill";
      repeat.textContent = "每天";
      titleRow.append(repeat);
    }

    if (todo.remind && todo.time) {
      const remind = document.createElement("span");
      remind.className = "remind-pill";
      remind.textContent = "提醒";
      titleRow.append(remind);
    } else if (todo.time && !todo.done) {
      const noRemind = document.createElement("span");
      noRemind.className = "no-remind-pill";
      noRemind.textContent = "不提醒";
      titleRow.append(noRemind);
    }

    if (todo.tag) {
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = `#${todo.tag}`;
      titleRow.append(tag);
    }

    const meta = document.createElement("div");
    meta.className = "todo-meta";
    meta.textContent = `记录于 ${formatDateTime(todo.createdAt)}`;

    const note = document.createElement("textarea");
    note.className = "note";
    note.placeholder = "补充备注";
    note.value = todo.note || "";
    note.addEventListener("input", () => updateNoteDebounced(todo, note.value));

    main.append(titleRow, meta, note);

    const actions = document.createElement("div");
    actions.className = "todo-actions";

    if (todo.source === "recurring") {
      const stopButton = document.createElement("button");
      stopButton.type = "button";
      stopButton.className = "stop-btn";
      stopButton.textContent = "停";
      stopButton.title = "从今天起终止每天重复";
      stopButton.addEventListener("click", () => {
        stopRecurringTodo(todo);
        render();
      });
      actions.append(stopButton);
    }

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-btn";
    deleteButton.textContent = "删";
    deleteButton.title = "删除";
    deleteButton.addEventListener("click", () => {
      deleteTodo(todo);
      render();
    });
    actions.append(deleteButton);

    item.append(checkButton, main, actions);
    elements.todoList.append(item);
  });
}

function updateNoteDebounced(todo, note) {
  const key = `${todo.source}-${todo.instanceDate || state.selectedDate}-${todo.id}`;
  window.clearTimeout(state.noteTimers.get(key));
  state.noteTimers.set(
    key,
    window.setTimeout(() => {
      updateTodo(todo, { note });
      state.noteTimers.delete(key);
    }, 650)
  );
}

function formatDateLabel(dateKey) {
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "long",
  }).format(fromDateKey(dateKey));
}

function shiftDay(offset) {
  const date = fromDateKey(state.selectedDate);
  date.setDate(date.getDate() + offset);
  state.selectedDate = toDateKey(date);
  render();
}

function renderNotificationStatus() {
  if (state.backgroundAvailable) {
    elements.notificationStatus.textContent = "后台提醒已连接：关闭网页后仍会发送 Windows 通知，并在系统托盘保留后台图标。";
    elements.enableNotificationsBtn.disabled = true;
    elements.testNotificationBtn.disabled = false;
    return;
  }

  if (!supportsSystemNotifications()) {
    elements.notificationStatus.textContent = "当前浏览器不支持系统通知。";
    elements.enableNotificationsBtn.disabled = true;
    elements.testNotificationBtn.disabled = true;
    return;
  }

  const permission = Notification.permission;
  const statusText = {
    granted: "系统通知已启用，到点会进入 Windows 通知中心。",
    denied: "系统通知已被阻止，请在浏览器网站权限或 Windows 通知设置里重新允许。",
    default: "系统通知尚未启用，请先点击“启用系统通知”。",
  };

  elements.notificationStatus.textContent = statusText[permission] || "无法读取系统通知权限。";
  elements.enableNotificationsBtn.disabled = permission === "granted" || permission === "denied";
  elements.testNotificationBtn.disabled = permission !== "granted";
}

function supportsSystemNotifications() {
  return "Notification" in window && window.isSecureContext;
}

async function enableSystemNotifications() {
  if (!supportsSystemNotifications()) {
    showToast("当前打开方式不支持系统通知。建议用 http://127.0.0.1 或 localhost 打开。");
    renderNotificationStatus();
    return;
  }

  const permission = await Notification.requestPermission();
  renderNotificationStatus();

  if (permission === "granted") {
    showSystemNotification("每日待办通知已启用", "之后到点提醒会进入 Windows 通知中心。");
    showToast("系统通知已启用。");
    return;
  }

  if (permission === "denied") {
    showToast("系统通知被阻止了，请到浏览器或 Windows 通知设置里允许。");
    return;
  }

  showToast("还没有启用系统通知。");
}

function testSystemNotification() {
  if (state.backgroundAvailable) {
    fetch(SERVER_TEST_NOTIFICATION_URL, { cache: "no-store" })
      .then((response) => {
        if (!response.ok) throw new Error("Test notification failed");
        showToast("已发送后台测试通知，留意 Windows 通知中心和系统托盘图标。");
      })
      .catch(() => {
        state.backgroundAvailable = false;
        renderNotificationStatus();
        showToast("后台提醒服务暂时不可用。");
      });
    return;
  }

  const ok = showSystemNotification("每日待办测试通知", "如果你看到了这条，Windows 系统通知已经接通。");
  showToast(ok ? "已发送测试通知。" : "测试通知未发送：请先启用系统通知。");
  renderNotificationStatus();
}

function checkReminders() {
  const now = new Date();
  const today = toDateKey(now);
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  getDayTodos(today).forEach((todo) => {
    if (!todo.time || !todo.remind || todo.done) return;
    const [hours, minutes] = todo.time.split(":").map(Number);
    const todoMinutes = hours * 60 + minutes;
    const key = `${today}-${todo.id}-${todo.time}`;
    if (currentMinutes >= todoMinutes && currentMinutes <= todoMinutes + 5 && !state.notified.has(key)) {
      state.notified.add(key);
      notify(todo);
    }
  });
}

function notify(todo) {
  const message = `${todo.time} ${todo.title}`;
  showSystemNotification("待办提醒", message);
  showToast(`待办提醒：${message}`);
}

function showSystemNotification(title, body) {
  if (!supportsSystemNotifications() || Notification.permission !== "granted") return false;
  new Notification(title, {
    body,
    tag: `daily-todo-${title}-${body}`,
    renotify: true,
    requireInteraction: true,
  });
  return true;
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => elements.toast.classList.remove("show"), 4200);
}

function formatDateTime(value) {
  if (!value) return "";
  return new Date(value).toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function isDueSoon(todo) {
  if (state.selectedDate !== toDateKey(new Date()) || !todo.time || todo.done) return false;
  const now = new Date();
  const [hours, minutes] = todo.time.split(":").map(Number);
  const diff = hours * 60 + minutes - (now.getHours() * 60 + now.getMinutes());
  return diff >= 0 && diff <= 30;
}


elements.todoForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const title = elements.titleInput.value.trim();
  if (!title) return;

  addTodo({
    title,
    time: elements.timeInput.value,
    priority: elements.priorityInput.value,
    tag: elements.tagInput.value.trim(),
    remind: elements.remindInput.checked,
    repeatDaily: elements.repeatInput.checked,
  });

  elements.todoForm.reset();
  elements.priorityInput.value = "normal";
  elements.remindInput.checked = true;
  elements.titleInput.focus();
  render();
});

elements.dateInput.addEventListener("change", () => {
  state.selectedDate = elements.dateInput.value || toDateKey(new Date());
  render();
});

elements.prevDay.addEventListener("click", () => shiftDay(-1));
elements.nextDay.addEventListener("click", () => shiftDay(1));
elements.todayBtn.addEventListener("click", () => {
  state.selectedDate = toDateKey(new Date());
  render();
});

elements.searchInput.addEventListener("input", () => {
  state.search = elements.searchInput.value;
  render();
});

elements.filters.forEach((button) => {
  button.addEventListener("click", () => {
    state.filter = button.dataset.filter;
    render();
  });
});

elements.enableNotificationsBtn.addEventListener("click", enableSystemNotifications);
elements.testNotificationBtn.addEventListener("click", testSystemNotification);

render();
loadServerStore();
checkReminders();
window.setInterval(checkReminders, 30 * 1000);
