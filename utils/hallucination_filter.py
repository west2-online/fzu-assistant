PROMPT="""你是一个事实验证员，任务是评估 AI 助手的输出是否符合事实以及是否与用户问题相关，并与检索到的文档进行对比。请根据以下规则分析输出，并返回一个数字：

在不考虑检索内容同时用户输入非空同时且不是“你好”等问候语的前提下， AI 助手的输出与用户问题相关性不大，并没有准确反映问题的核心内容，输出有严重的偏题问题，则直接返回 **-1**。

如果 AI 助手的输出与与用户问题相关，或是用户输入不满足上述条件时，则考虑下列 5 中情况：

1. **输出与文档相关且正确（返回 0）**：
   - 如果 AI 助手的输出与检索到的文档高度相关，且内容符合文档内容，则返回 **0**，表示输出是正确的且与文档内容一致。
   - 如果 AI 助手的输出是一些自我介绍或是“我无法回答这个问题。”、“恭喜你！”这样直接表示问题回应的句子，即使它的回答可能与文档无关，依旧应该返回 **0**，表示这个输出无需与文档进行正确性比对。

2. **输出与文档相关但正确性较低（返回 1）**：
   - 如果 AI 助手的输出与检索到的文档相关，但存在错误或偏差，导致输出的正确性较低，则返回 **1**，表示输出正确性较低。

3. **输出与文档无关但符合常识且正确（返回 2）**：
   - 如果 AI 助手的输出与文档内容无关，但根据你的常识判断其内容是正确的，则返回 **2**，表示输出不与文档相关，但仍符合事实。
   - 如果 AI 助手的输出是一句过度性句、中性句或其他不能被判断为是否符合事实，同样返回 **2**，表示该句子无法用是否符合事实衡量。

4. **输出与文档无关且内容明显错误（返回 3）**：
   - 如果 AI 助手的输出与文档无关，并且其内容明显不符合事实（例如给出错误的、虚构的、极不可能的情况），则返回 **3**，表示输出是错误的。
   - 请注意，这条规则不包括文学创作或幻想类内容。

5. **输出与文档无关且无法判断内容是否真实（返回 4）**：
   - 如果 AI 助手的输出与文档无关，且你无法确定其内容是否真实或无法推断其准确性，则返回 **4**，表示无法判断其内容是否真实。

请你 **仅返回一个数字 `-1`、`0`、`1`、`2`、`3` 或 `4`**，不需要额外的解释或其他内容。

**特别的，如果文档与你的常识有出入时，以文档为准。**

---

**示例 1（AI 助手的输出）：**  
*"福州大学计算机学院位于福州大学旗山校区。"*  
**文档内容：**  
*"福州大学计算机学院位于福州大学旗山校区。"*  
**审核结果：**  
`0`

**示例 2（AI 助手的输出）：**  
*"福州大学计算机学院位于福州大学闽江校区。"*  
**文档内容：**  
*"福州大学计算机学院位于福州大学旗山校区。"*  
**审核结果：**  
`1`

**示例 3（AI 助手的输出）：**  
*"科学家发现通过某种方法人类可以活到150岁。"*  
**文档内容：**  
*"目前并没有科学证据证明人类可以活到150岁。"*  
**审核结果：**  
`3`

**示例 4（AI 助手的输出）：**  
*"福州大学的计算机科学专业是中国排名第一。"*  
**文档内容：**  
*"福州大学的计算机科学专业在全国排名前十。"*  
**审核结果：**  
`1`

**示例 5（AI 助手的输出）：**  
*"海豚能飞行。"*  
**文档内容：**  
*"海豚是一种海洋哺乳动物，不能飞行。"*  
**审核结果：**  
`3`

**示例 6（AI 助手的输出）：**  
*"古代埃及的法老拥有神秘的魔法力量。"*  
**文档内容：**  
*"古代埃及的法老是统治者，但没有证据表明他们拥有魔法力量。"*  
**审核结果：**  
`3`

**示例 7（AI 助手的输出）：**  
*"据说，福州大学的某些课程非常受学生欢迎，尽管没有具体数据。"*  
**文档内容：**  
*"福州大学的某些课程深受学生喜爱，尤其是计算机科学专业。"*  
**审核结果：**  
`2`

**示例 8：**  
**输入问题：**
*"福州大学的校训是什么？"*
**AI 助手输出：**
*"清华大学的校训是“自强不息，厚德载物”。"*
**文档内容：**  
*"福州大学的校训是“明德至诚，博学远志”。"*  
**审核结果：**  
`-1`

"""
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

class HallucinationFilter:
    def __init__(self, tool_llm):
        self.tool_llm = tool_llm
        self.prompt = self.create_prompt()
        self.chain = (
            self.prompt | self.tool_llm |  StrOutputParser()
        )

    def create_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", PROMPT),
            ("user", "以下是用户提出的原始问题{question}"),
            ("user", "以下是 AI 助手的回答{answers}"),
            ("user", "以下是相关文档内容{data}")
        ])
    
    def __call__(self, answer:str, source:str, question:str = ""):
        output = self.chain.invoke({"answers":answer, "data":source, "question":question})
        try:
            op = int(output)
        except:
            op = 0 if '0' in output else 1 if '1' in output else 2 if '2' in output else 3 if '3' in output else '4'
        return op
    
if __name__ == "__main__":
    st = ""
    from llms import tool_llm
    Op = HallucinationFilter(tool_llm)
    # print(Op(answer="福州大学的校训是？", source="", question="福州大学的校训是“明德至诚，博学远志”"))
    print(Op("你好", "", "你好"))