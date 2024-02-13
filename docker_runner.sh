docker run  \
-it \
--platform linux/amd64 \
-v ~/.aws:/root/.aws \
-v images:/home/seluser/images \
-e platform='yandex' \
-e image_path='/home/seluser/images/public_photo.jpg' \
avliu/monitor-images:latest \
bash

#docker buildx build --platform linux/amd64 -t avliu/monitor-images:vXXX .