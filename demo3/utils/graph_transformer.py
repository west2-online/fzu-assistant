from langchain.prompts import ChatPromptTemplate
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents import Document
from langchain_core.messages.ai import AIMessage
from pydantic import BaseModel
from tqdm import tqdm
import typing as t
import json
import re


from pydantic import BaseModel


class EntitySchema(BaseModel):
    entity: str
    entity_type: str


class RelationSchema(BaseModel):
    start_entity: EntitySchema
    relation: str
    end_entity: EntitySchema


class GraphSchema(BaseModel):
    entities: t.List[EntitySchema]
    relations: t.List[RelationSchema]


class GraphTransformer:
    def __init__(self, llm, prompt: t.Optional[ChatPromptTemplate] = None, schema: t.Optional[BaseModel] = None):
        self.prompt = prompt or self.create_prompt()
        self.schema = schema or GraphSchema
        self.parser = self.create_parser()
        self.chain = self.prompt | llm | self.parser

    def convert_to_graph_documents(self, documents: t.List[Document]) -> t.List[GraphDocument]:
        return [self.process_response(document=document) for document in tqdm(documents)]

    def process_response(self, document: Document) -> GraphDocument:
        raw_result = self.chain.invoke({"text": document.page_content})
        json_result = json.loads(raw_result.model_dump_json())
        nodes_set = set()
        relationships = []
        # for ent in json_result.get("entities"):
        #     entity = ent.get("entity")
        #     entity_type = ent.get("entity_type")
        #     # nodes_set.add((entity, entity_type))

        for rel in json_result.get("relations"):
            start_entity = rel.get("start_entity").get("entity")
            start_entity_type = rel.get("start_entity").get("entity_type")
            relation = rel.get("relation")
            end_entity = rel.get("end_entity").get("entity")
            end_entity_type = rel.get("end_entity").get("entity_type")

            nodes_set.add((start_entity, start_entity_type))
            nodes_set.add((end_entity, end_entity_type))
            relationships.append(
                Relationship(
                    source=Node(id=start_entity, type=start_entity_type),
                    target=Node(id=end_entity, type=end_entity_type),
                    type=relation
                )
            )
            # print((start_entity, start_entity_type) , "-[", relation, "]-", (end_entity, end_entity_type))
        nodes = [Node(id=el[0], type=el[1]) for el in list(nodes_set)]

        return GraphDocument(nodes=nodes, relationships=relationships, source=document)

    def create_prompt(self) -> ChatPromptTemplate:
        system_msg = """# 我需要你根据文本提取出实体以及实体之间的关系。
        ## 输出要求
        - 实体：明确指出文本中出现的所有具有特定意义的名词或名词短语，如人名、地名、组织名等。相似的实体请归纳为一种。
        - 关系：准确描述实体之间的联系，关系词要能清晰表达这种联系，例如“拥有”“属于”“位于”等。相似的关系请选择最常见的那一种。
        - 输出格式：
          - "实体：{entity}({entity_type})"
          - "关系：{start_entity}({start_entity_type})-{relation}-{end_entity}({end_entity_type})"
        
        以下是一个示例，帮助你理解任务和回答格式：
        文本："张三在苹果公司工作"
        回答：
        "实体：张三(人名)"
        "实体：苹果公司(组织)"
        "关系：张三(人名)-属于-苹果公司(组织)"
        """
        human_msg = """
        文本："{text}"
        回答：
        """

        prompt = ChatPromptTemplate(
            messages=[
                ("system", system_msg),
                ("human", human_msg)
            ],
            input_variables=["text"],
            partial_variables={
                "entity": "{实体}",
                "entity_type": "{实体类型}",
                "start_entity": "{起点实体}",
                "start_entity_type": "{起点实体类型}",
                "relation": "{关系}",
                "end_entity": "{终点实体}",
                "end_entity_type": "{终点实体类型}"
            })
        return prompt

    def create_parser(self) -> t.Callable:
        def er_parser(result: t.Union[AIMessage, str]) -> GraphSchema:
            # print(type(result))
            content: str = result if isinstance(result, str) else result.content
            lines = content.split("\n")
            entity_pattern = re.compile(r"实体：([^(（]+)[（(]([^)）]+)[）)]")
            relation_pattern = re.compile(
                r"关系：([^(（]+)[（(]([^)）]+)[）)]-([^-—]+)(—|-)([^(（]+)[（(]([^)）]+)[）)]"
            )
            entity_store = {}
            relations = []

            for line in lines:
                line = line.strip().strip('"')
                if line.startswith("实体："):
                    match = entity_pattern.search(line)
                    if match:
                        entity_name, entity_type = match.groups()
                        key = (entity_name.strip(), entity_type.strip())
                        if key not in entity_store:
                            entity_store[key] = EntitySchema(entity=key[0], entity_type=key[1])
                elif line.startswith("关系："):
                    match = relation_pattern.search(line)
                    if match:
                        (
                            start_name,
                            start_type,
                            relation,
                            _,
                            end_name,
                            end_type
                        ) = match.groups()

                        start_name = start_name.strip()
                        start_type = start_type.strip()
                        end_name = end_name.strip()
                        end_type = end_type.strip()
                        relation = relation.strip()

                        start_entity = entity_store.get((start_name, start_type))
                        end_entity = entity_store.get((end_name, end_type))

                        if start_entity and end_entity:
                            relations.append(
                                RelationSchema(
                                    start_entity=start_entity,
                                    relation=relation,
                                    end_entity=end_entity,
                                )
                            )

            return self.schema(
                entities=list(entity_store.values()),
                relations=relations
            )

        return er_parser


if __name__ == "__main__":
    from langchain_mistralai import ChatMistralAI
    mistral = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0,
        max_retries=2
    )
    llm_transformer = GraphTransformer(mistral)

    text = """
    # 寝室生活 ## 铜盘 寝室外配备了共享洗衣机，隔层有饮水机； 浴室与厕所干湿分离； 一人一套“上床下桌”：床铺宽90cm，长200cm，蚊帐架高110cm； ## 旗山 洗衣机需自购；饮水可以订购桶装水，买一个电动抽水装上比较便宜； 浴室与厕所不干湿分离，在同一间； 一人一套“上床下桌”：床铺宽90cm，长195cm，蚊帐架高110cm，不过部分床位的蚊帐架可能被拆除； 搬到旗山后，宿舍位置大概率不会再改变，可以买一架电脑椅提高舒适度！计算机专业的同学也可以购置一台24寸或者27寸的显示器； 宿舍家具损坏报修需要前往 智汇福大app->我的服务->公寓报修，一般情况下第二天就会有维修人员上门维修； 旗山宿舍的桌子不会像铜盘那么干净，可以贴上桌面贴纸或者铺上桌垫； <Callout type="info"> (非广告,自用的) 旗山校区送水微信: wwww_968968, 手机: 150 8007 1312 会直接给你送水到宿舍门口(不论几层), 桶押金不超过 30, 一桶水 15, 可以喝约半个月(按 4 人算)
    """
    documents = [Document(text)]
    graph_documents = llm_transformer.convert_to_graph_documents(documents)
    print(graph_documents)