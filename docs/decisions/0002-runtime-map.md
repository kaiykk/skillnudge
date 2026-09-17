# Decision

冻结 V0 Runtime Map：

```text
Input
→ Capability
→ Intervention
→ Query
→ Candidate Acquisition
→ Evidence
→ Judge
→ Advice
```

# Context

如果在没有边界的情况下直接实现“推荐 Skill”，很容易把理解、检索、判断
和最终表达混在一个不可复查的调用里。

# Options considered

- 单个 prompt 直接输出推荐；
- 只做 Query → Search；
- 采用分层 Runtime，并让 Trace 横切每一层。

# Decision

采用分层 Runtime。每层有明确职责，Candidate Acquisition 不直接产生
Final Advice，Trace 横切整个流程。

# Why

分层后可以分别判断理解错、路由错、检索错、证据不足和判断错，而不必把
所有失败归因给一个黑盒模型。

# Consequences

- 实现需要维护中间对象；
- 每层都要定义输入、输出和不确定性；
- 不能为了快速 demo 把所有逻辑合并成一个函数。

# Revisit when

如果小规模实验显示分层记录成本明显高于诊断收益，再重新评估最小边界。

