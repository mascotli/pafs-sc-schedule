# pafs-sc-algorithm

This project was generated via [manage-fastapi](https://ycd.github.io/manage-fastapi/)! :tada:

## License

This project is licensed under the terms of the GNU license.

## run

```shell
uvicorn app.main:app --port 8000 --reload
```

## requirements

```shell
# install requirements.txt
pip install -r requirements.txt 

# generate requirements.txt

# 1. 使用pipreqs它会根据当前目录下的项目的依赖来导出三方类库
# pip install pipreqs
pipreqs ./ --encoding=utf8 --force

# 2. 使用pip freeze保存的是当前Python环境下所有的类库
pip freeze > requirements.txt
```

## docker

- build

```shell
# build image
docker build -t pafs-sc-algorithm:v1 ./

# run
docker run -d -p 8000:8000 --network recharde-bridge pafs-sc-algorithm:v1
```

- [镜像瘦身](https://www.jianshu.com/p/c0ad13e0be85)

## env

- [多环境变量](https://yanbin.blog/python-multi-envs-configurations/#more-12901)

## dev

- [log](https://www.jianshu.com/p/5e3086ed5842)