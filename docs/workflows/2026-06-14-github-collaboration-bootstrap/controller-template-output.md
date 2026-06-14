# Controller Template Output

## Verified Conclusion

This workflow is reusable for similar local-to-GitHub project onboarding tasks.

The successful sequence was:

1. Human provided the objective, local path, and remote repository.
2. Controller performed read-only discovery first.
3. Controller created durable workflow state and role boundaries.
4. Architect produced a bootstrap plan.
5. Developer implemented collaboration files and initialized Git.
6. Acceptance Tester verified local tests, ignore rules, remote state, PR flow, and CI.
7. Controller reconciled evidence and closed the loop.

## Human-To-Controller Prompt Template

```text
你现在是本项目的组长 Controller。请按多角色软件开发工作流推进，直到得到验证过的结论。

项目目标：
【一句话说明要完成什么】

本地项目路径：
【绝对路径】

远程仓库：
【GitHub URL；如果没有就写“暂无”】

当前阶段：
【项目启动前 / 项目开发中 / 项目开发完成后 / 协作验证中】

请你先做：
1. 只读盘点本地项目、Git 状态、远程仓库状态、测试入口和风险文件。
2. 建立或更新 workflow 控制面文件。
3. 注册角色：Controller、Architect、Developer、Acceptance Tester。
4. 先让 Architect 输出方案，再让 Developer 实施，最后让 Acceptance Tester 验收。
5. 自己运行必要测试，不要只相信角色自述。
6. 把最终验证结果、剩余风险和可复用结论输出给我。

授权边界：
- 允许：为了完成目标进行本地文件修改、初始化 Git、创建分支、提交、推送、创建 PR、等待 CI、合并验证性 PR。
- 禁止：删除用户数据、提交 secrets、提交本地运行数据、重写已完成产品功能、无需求重构、添加不必要依赖、改生产环境。
- 如果遇到会改变产品方向、删除数据、迁移架构、引入付费服务或暴露隐私的动作，必须停下来问我。

验收标准：
- 新目标完成。
- 现有相关功能未被破坏。
- 本地测试通过。
- 远程 GitHub 状态可验证。
- CI 通过，或失败原因被明确记录。
- 工作区干净，只剩明确被忽略的本地数据/缓存。
```

## Human Work Boundary

Humans should own product intent and risk decisions:

- Say what outcome is wanted.
- Provide local path and remote location.
- Decide whether data may be published, migrated, deleted, or anonymized.
- Decide product scope, launch scope, and acceptance priorities.
- Decide whether paid services, public repositories, or production mutations are allowed.
- Review final conclusions and choose the next product direction.

Humans should not need to:

- Manually copy prompts between roles for every step.
- Inspect every file before the Controller starts discovery.
- Know Git internals before asking for GitHub collaboration.
- Personally run every test when the Controller can run and report them.

## Controller Boundary

The Controller should own workflow integrity:

- Convert human intent into a clear objective and acceptance criteria.
- Discover current state before editing.
- Create durable workflow files.
- Assign Architect, Developer, and Acceptance Tester responsibilities.
- Keep authorization boundaries explicit.
- Reconcile role outputs with actual command evidence.
- Continue autonomously when the user has granted the boundary.
- Stop only for true blockers or decisions that belong to the human.

## Role Boundary

Architect:

- Designs the approach.
- Lists affected files and risks.
- Defines verification strategy.
- Does not implement product changes.

Developer:

- Implements the approved slice.
- Keeps changes scoped.
- Runs local verification.
- Writes a handoff with changed files and proof.

Acceptance Tester:

- Verifies behavior and workflow evidence independently.
- Checks local tests, Git status, remote state, PR/CI state, and residual risks.
- Does not accept work based only on a developer summary.

## Copyability Assessment

This workflow is enough to copy to different projects when these inputs exist:

- clear local project path
- clear target outcome
- known remote or desired remote policy
- permission boundary for GitHub mutation
- at least one verification command or a willingness to create minimal verification

It needs adjustment when:

- the project contains production secrets
- the project has a database or migrations
- CI requires paid/external services
- multiple agents need simultaneous product edits
- the repository already has history, branches, issues, or active PRs
- the project is not safe to publish publicly

## Practical Default

For a non-expert human, the best default is:

- Human gives goal, path, remote, and permission boundary.
- Controller owns discovery and orchestration.
- Architect plans first.
- Developer implements one small verified slice.
- Acceptance Tester verifies from evidence.
- Controller summarizes decisions and next steps.
