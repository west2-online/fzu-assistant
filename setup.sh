# download models
export HF_ENDPOINT="https://hf-mirror.com"
# until huggingface-cli download deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --local-dir ./models/DeepSeek-R1-Distill-Qwen-1.5B; do : ; done
until huggingface-cli download deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --local-dir ./models/DeepSeek-R1-Distill-Qwen-7B; do : ; done
until huggingface-cli download TencentBAC/Conan-embedding-v1 --local-dir ./models/Conan-embedding-v1; do : ; done
until huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir ./models/Qwen2.5-7B-Instruct; do : ; done


# neo4j
## java env
sudo apt install openjdk-11-jdk

## download
# curl -O https://dist.neo4j.org/neo4j-community-4.4.41-unix.tar.gz neo4j.tar.gz
tar -xf neo4j-community-4.4.41-unix.tar.gz
mv neo4j-community-4.4.41 nj
sed -i '/#dbms.security.auth_enabled/s/^#//g' nj/conf/neo4j.conf

## use apoc
mv nj/labs/apoc-4.4.0.35-core.jar nj/plugins/
echo "dbms.security.procedures.unrestricted=apoc.*" >> nj/conf/neo4j.conf
echo "apoc.import.file.enabled=true" >> nj/conf/neo4j.conf
echo "apoc.export.file.enabled=true" >> nj/conf/neo4j.conf
echo "dbms.default_listen_address=0.0.0.0" >> nj/conf/neo4j.conf

# 防火墙
sudo ufw allow 7474
sudo ufw allow 7687

## run
nj/bin/neo4j start