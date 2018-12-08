FROM python:3.6

RUN apt-get update
RUN apt-get install -y busybox-static
RUN apt-get clean

# タイムゾーン設定
ENV TZ=Asia/Tokyo

ARG project_dir=/work

# 必要なファイルをローカルからコンテナにコピー
RUN mkdir -p $project_dir

# requirements.txtに記載されたパッケージをインストール                         
WORKDIR $project_dir
ADD ./cron.edit /var/spool/cron/crontabs/root
ADD ./run.sh $project_dir
RUN chmod 700 $project_dir/run.sh

ADD ./requirements.txt $project_dir
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# busybox crond -f -L /dev/stderr
CMD ["busybox", "crond", "-f", "-L", "/dev/stderr"]