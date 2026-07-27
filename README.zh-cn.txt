# PowerPoint 互动游戏生成器
> 通过占位文本框生成拖拽式和输入式提示游戏

## 本地生成 - Docker Hub
- https://hub.docker.com/r/xp6qhg9fmuolztbd2ixwdbtd1/ppt-interactive-generator-server
1. 运行 `sudo docker pull xp6qhg9fmuolztbd2ixwdbtd1/ppt-interactive-generator-server`
2. 运行：
```
sudo docker rm "public-ppt-interactive-generator-server" -f || echo "failed to remove existing server" && \
sudo docker run -dit --restart="always" --name "public-ppt-interactive-generator-server" \
--mount type=bind,source=/home/morphs/DOCKER_IMAGES/PowerPointInteractiveGameGenerator/config.json,target=/home/config.json \
-p 17393:9379 xp6qhg9fmuolztbd2ixwdbtd1/ppt-interactive-generator-server config.json
```
3. 打开 http://localhost:17393/local

## 本地生成 - 构建 Docker 服务器

1. 构建 Docker 镜像 `./dockerBuild.sh`
2. 编辑 `./dockerBuild.sh`，填写 config.json 的正确绝对路径
3. 运行 `./dockerRun.sh`
4. 打开 http://localhost:17393/local

## 托管图片和 HTML 的生成方式

1. 运行 `python3 01_prepare_powerpoint.py input.pptx config.json`
2. 将 input.pptx 导出为 JPEG 图片
4. 运行 `python3 02_upload_and_generate_powerpoint.py input.pptx config.json`

### 结果

![](https://39363.org/IMAGE_BUCKET/1636526211492-992772358.png)

- https://39363.org/CDN/MISC/ExampleDragAndDrop.html
- https://39363.org/CDN/MISC/ExampleTyping.html
- 在输入模式下：
	- `Control` = 显示提示
	- `Control + Z` = 自动输入当前标签

### 待办事项 (Todo)

- 添加返回按钮
- 根据视口大小自动调整图片缩放百分比
- 根据最长单词的长度调整拖拽模式的 bootstrap 列宽
- 修复正确答案误触两次拖拽导致计数过多的问题
- 添加点击编辑任意文本框的功能
- 推算每个文本框的字体大小
