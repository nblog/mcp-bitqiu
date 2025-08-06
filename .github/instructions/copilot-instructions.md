## 🎯 核心协作原则

### 1. 需求澄清优先
- **模糊问题时，多提问而非急于解决**
- 通过**递增式明确目标**，逐步细化需求
- 双方达成一致建议后再开始实施
- 避免基于假设进行开发

### 2. 代码质量至上
- 发现更优雅的实现时，**必须主动提出**
- 支持为了提高可读性而进行重构
- 优先考虑代码的长期维护性
- 追求简洁、清晰、易懂的代码风格
- 遵循 **DRY** 原则，避免重复性维护

## 🏗️ 编程偏好与规范

### 数据结构与序列化
- **强烈偏好结构化数据定义**
  - 使用 `Pydantic` 等工具定义数据模型
  - 避免过度依赖字典的"记忆性"键值访问
  - 优先类型安全的序列化/反序列化方案
  - 内置显示逻辑，避免外部转换散布

```python
# ✅ 推荐方式：内置显示逻辑
from pydantic import BaseModel
from enum import Enum

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
  
    def __str__(self) -> str:
        return self.value.title()
  
    @property
    def display_text(self) -> str:
        mapping = {
            self.ACTIVE: "✅ 已激活",
            self.INACTIVE: "❌ 已停用", 
            self.PENDING: "⏳ 待处理"
        }
        return mapping[self]

class UserProfile(BaseModel):
    name: str
    age: int
    email: str
    status: Status
  
    def __str__(self) -> str:
        return f"{self.name} ({self.status})"
  
    def __repr__(self) -> str:
        return f"UserProfile(name='{self.name}', status={self.status!r})"
  
    @property
    def display_text(self) -> str:
        return f"用户: {self.name} | 状态: {self.status.display_text}"

# 使用时直接调用，无需外部映射
user = UserProfile(name="张三", age=25, email="zhang@example.com", status=Status.ACTIVE)
print(user.display_text)  # "用户: 张三 | 状态: ✅ 已激活"

# ❌ 避免方式：外部映射散布各处
user_data = {"name": "张三", "status": "active"}
# 在模板中
status_map = {"active": "✅ 已激活", "inactive": "❌ 已停用"}  # 硬编码映射
display = f"状态: {status_map.get(user_data['status'], '未知')}"
# 在另一个文件中又重复定义相同映射...
```

### 数据一致性与维护性
- **单一数据源原则**
  - 避免在多处硬编码相同的值或逻辑
  - 显示逻辑集中在数据定义处，避免散布各处
  - 通过引用确保数据的一致性
  - 设计时考虑未来的扩展和修改

```python
# ✅ 推荐：显示逻辑与数据定义保持同步
from enum import Enum

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
  
    def __str__(self) -> str:
        return self.name.title()
  
    @property
    def display_text(self) -> str:
        icons = {
            self.LOW: "🟢 低优先级",
            self.MEDIUM: "🟡 中优先级", 
            self.HIGH: "🟠 高优先级",
            self.CRITICAL: "🔴 紧急处理"
        }
        return icons[self]
  
    @property
    def sort_weight(self) -> int:
        return self.value

# 验证和显示都引用同一定义
def validate_priority(priority_str: str) -> Priority:
    try:
        return Priority[priority_str.upper()]
    except KeyError:
        valid_options = ", ".join([p.name.lower() for p in Priority])
        raise ValueError(f"优先级必须是: {valid_options}")

# ❌ 避免：多处硬编码显示逻辑
# models.py
PRIORITY_CHOICES = [(1, "low"), (2, "medium"), (3, "high"), (4, "critical")]

# views.py
PRIORITY_DISPLAY = {1: "🟢 低", 2: "🟡 中", 3: "🟠 高", 4: "🔴 紧急"}  # 重复定义

# templates.py
priority_icons = {"low": "🟢", "medium": "🟡", ...}  # 又一次重复
```

### 代码组织与架构
- 清晰的项目结构和模块划分
- 合理的抽象层次和职责分离
- 数据模型负责自身的显示逻辑
- 优先使用类型提示和文档字符串
- 遵循 SOLID 原则和设计模式
- 集中管理配置、常量、枚举等定义

### 错误处理与日志
- 明确的异常处理策略
- 结构化的日志记录
- 优雅的错误恢复机制

## 💬 沟通与协作风格

### 问题分析流程
1. **理解阶段**: 澄清需求和约束条件
2. **规划阶段**: 制定技术方案和实施计划
3. **确认阶段**: 双方达成一致后开始实施
4. **迭代阶段**: 根据反馈持续改进

### 建议提出方式
- 主动指出潜在的优化点
- 提供多种解决方案供选择
- 解释技术决策的利弊权衡
- 考虑未来扩展性和维护成本
- 发现显示逻辑散布时立即建议封装到数据模型
- 发现重复性维护点时立即提出重构建议

## 🔧 技术栈偏好

### 开发工具
- **Python包和项目管理器**: [uv](https://docs.astral.sh/uv/getting-started/)

```bash
uv add httpx
uv add pytest --optional dev
uv run python main.py
```

- **AI框架**: [semantic-kernel](https://github.com/microsoft/semantic-kernel/tree/main/python/)

  1. semantic-kernel
  ```python
  class ChatSession:
      async def init_agents(self):
          agent_tool = ChatCompletionAgent(
              ...
      async def user_input(self, user_input: str):
          ...

  async def main():
      from aioconsole import ainput

      session = ChatSession()

      while 1:
          try:
              user_input = await ainput("\n# user:> ")
              if len(user_input) < 1:
                  continue

              if user_input.startswith("/bye"):
                  raise KeyboardInterrupt
          except (KeyboardInterrupt, EOFError):
              sys.exit(0)

          response = await session.user_input(user_input)
          print(f"\n# {message.role} - {message.name or '*'}: '{message.content}'")
  ```

  2. semantic-kernel [mcp server](https://github.com/microsoft/semantic-kernel/tree/main/python/samples/concepts/mcp)
  ```python
  def run(transport: Literal["sse", "stdio"] = "stdio", port: int | None = None) -> None:
    kernel = Kernel()

    @kernel_function()
    def echo(input: str) -> str:
      return f"Echo: {input}"

    kernel.add_function("__builtins__", echo)
    server = kernel.as_mcp_server(server_name="sk-mcp-server")

    if transport == "sse" and port is not None:
      import uvicorn
      from mcp.server.sse import SseServerTransport
      from starlette.applications import Starlette
      from starlette.routing import Mount, Route

      ...

      uvicorn.run(starlette_app, host="0.0.0.0", port=port)  # nosec
    elif transport == "stdio":
      import anyio
      from mcp.server.stdio import stdio_server

      ...

      anyio.run(handle_stdin)
  ```

## 📋 代码审查清单

### 结构化数据
- [ ] 是否使用了类型安全的数据模型？
- [ ] 是否避免了过度使用字典存储结构化数据？
- [ ] 数据验证是否完整？
- [ ] 是否遵循了单一数据源原则？
- [ ] 是否实现了适当的 `__str__`、`__repr__` 方法？
- [ ] 复杂显示逻辑是否通过 `@property def display_text` 封装？

### 代码质量
- [ ] 代码是否足够清晰易读？
- [ ] 是否存在更优雅的实现方式？
- [ ] 错误处理是否完善？
- [ ] 是否有适当的类型提示？
- [ ] 是否存在重复的硬编码值或逻辑？
- [ ] 显示逻辑是否集中在数据模型而非散布各处？

### 维护性检查
- [ ] 修改枚举/常量时，是否需要同步更新多处代码？
- [ ] 验证逻辑是否直接引用了数据定义？
- [ ] 是否存在可以通过配置或引用统一管理的重复内容？
- [ ] 修改显示格式时，是否只需要在一处进行更改？
- [ ] 是否存在可以通过数据模型方法统一的显示转换？

### 架构设计
- [ ] 模块职责是否清晰？
- [ ] 是否遵循了设计原则？
- [ ] 扩展性如何？
- [ ] 测试覆盖率是否足够？
- [ ] 数据模型是否承担了适当的显示职责？

---

*本文档会根据项目进展和新的偏好持续更新*
