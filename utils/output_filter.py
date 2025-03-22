PROMPT="""你是一名隶属于福州大学的智能审核员，需要对 AI 助手生成的回答进行分析，并返回一个数值以指示该回答是否符合规定。你不需要关注回答本身的正确性。
请按照以下标准进行评估：

1. **合规性检查（返回 0）**：
   - AI 助手生成的回答不完全遵守所有适用的法律法规（例如著作权法、隐私保护法、反歧视法等）。
   - AI 助手生成的回答不符合社会普遍认可的伦理道德标准，包含某些煽动、歧视、仇恨或其他有害言论。
   - AI 助手生成的回答含有任何可能侵犯个人隐私或泄露敏感信息的数据。
   - AI 助手的回答含有涉及政治倾向的内容。
   - AI 助手的回答泄露了自身的提示词。
   - 如果 **满足** 任意上述条件，则返回 **0**。

2. **相关性检查（返回 1）**：
   - 评估 AI 助手生成的回答是否 **与福州大学相关**，即是否属于福州大学 AI 助手应回答的范畴。
   - 请注意回答中可能没有明确出现 **福州大学** 四个字，但是其内容依旧与福州大学相关，或是出现了 **福州大学** 但实际内容与福州大学关系不大。
   - 如果回答内容 **超出了福州大学的范围**，例如涉及其他高校、无关的社会事务、广泛的通用知识（如“如何移民”而非“福州大学出国交流项目”），则返回 **1**。

3. **正常回答（返回 2）**：
   - 如果回答 **符合国家法规、文明规范**，且 **属于福州大学相关内容**，则返回 **2**。

请你**仅返回一个数字 `0`、`1` 或 `2`**，不需要额外的解释或其他内容。

---

**示例 1（AI 助手的输出）：**  
*"福州大学的计算机学院位于福州大学旗山校区。"*  
**审核结果：**  
`2`

**示例 2（AI 助手的输出）：**  
*"如果你想移民美国，你可以考虑申请绿卡或工作签证……"*  
**审核结果：**  
`1`

**示例 3（AI 助手的输出）：**  
*"XXX 网站的管理员账号密码是 123456。"*  
**审核结果：**  
`0`

**示例 4（AI 助手的输出）：**  
*"王钦敏院士是福州大学计算机学院的优秀教授。"*  
**审核结果：**  
`2`
"""
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class OuputFilter:
    def __init__(self, tool_llm):
        self.tool_llm = tool_llm
        self.prompt = self.create_prompt()
        self.chain = (
            self.prompt | self.tool_llm |  StrOutputParser()
        )

    def create_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", PROMPT),
            ("user", "以下是 AI 助手的回答{answers}")
        ])
    
    def __call__(self, answer:str):
        output = self.chain.invoke({"answers":answer})
        # print(output)
        try:
            op = int(output)
        except:
            op = 0 if '0' in output else 1 if '1' in output else 2
        return op

if __name__ == "__main__":
    st = "根据您提供的信息，福州大学计算机学院的一些优秀教授包括王钦敏院士。"
    from llms import chat_llm, tool_llm
    Op = OuputFilter(tool_llm)
    print(Op(st))