# ベースイメージの指定
FROM python:3.6

RUN TZ=Asia/Tokyo
# ソースを置くディレクトリを変数として格納                                                  
ARG project_dir=/var/www

# 必要なファイルをローカルからコンテナにコピー
RUN mkdir -p $project_dir

# requirements.txtに記載されたパッケージをインストール                         
WORKDIR $project_dir
ADD ./requirements.txt $project_dir

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["uwsgi", "--ini", "/var/www/uwsgi.ini"]
