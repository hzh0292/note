**1、安装 git**

**debian/ubuntu**

sudo apt-get install git

**2、安装 pyenv**

***说明：本文的所有安装都严格遵守官方文档，与官方文档完全保持一致。***

git 地址：<https://github.com/pyenv/pyenv>

在你的终端中执行如下命令，安全无毒，请放心食用：

首先把项目克隆下来，放在家目录下的隐藏文件夹中：.pyenv

git clone https://github.com/pyenv/pyenv.git ~/.pyenv

然后配置环境变量

**依次执行如下命令：**

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc

echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc

echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init -)"\nfi' >> ~/.bashrc

echo 命令的含义是：将引号中内容写入某文件中

**ZSH:**

$ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc $ echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc $ echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.zshrc 

请注意，以上的三条 echo 命令的最后一条长长的命令，请你保证它引号中的内容处于 ~/.bashrc 的最底部。

因为在 pyenv 初始化期间会操作 path 环境变量，导致不可预测的行为。

查看文件的底部内容，可以使用 tail 命令，用法：tail ~/.bashrc 或者 tail ~/.zshrc，编辑文件可以使用 vim 或者 vscode

最后，在使用 pyenv 之前，重新初始化 shell 环境，执行如下命令

exec $SHELL

不执行该命令也是完全可以的，你可以关闭当前的终端窗口，重新启动一个就可以了。

此时，你已经完成了 pyenv 的安装了，你使用可以它的全部命令了，但是我建议你先别急着用，一口气装完 pyenv 的一个插件，那就是 pyenv-virtualenv

**3、安装 pyenv-virtualenv**

git 地址：<https://github.com/pyenv/pyenv-virtualenv>

把插件克隆在刚才已经安装完毕的 pyenv 的 plugins 文件夹中

git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv

然后配置环境变量

**执行如下命令：**

echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

**ZSH:**

$ echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc 

最后，在使用 pyenv 之前，重新初始化 shell 环境，执行如下命令

exec $SHELL

不执行该命令也是完全可以的，你可以关闭当前的终端窗口，重新启动一个就可以了。

到此，我们的所有重要安装已经全部完成了，可以开始体验了。

**使用 pyenv**

***此处仅仅展示 pyenv 和 virtualenv 的日常用法***

**检查安装是否正确**

显示 pyenv 的版本

pyenv --version

查看 pyenv 已经托管了哪些 python 版本

pyenv versions

查看 pyenv 当前python 版本

pyenv version

如果你看到了正常的版本信息，就说明可以了，如果看到了类似于 command not found 之类的，就说明安装失败了。

**安装 3.7.3 版本的 python**

pyenv install 3.7.3

这里有个问题，某些情况下会安装失败，报错就告诉你 Build failed

这个时候，pyenv 已经在它的 github wiki 里面为我们准备了一篇错误应对方案，原文地址 <https://github.com/pyenv/pyenv/wiki>

大意如下，只需要执行对应的命令即可：

**Ubuntu/Debian/Mint 用户**

sudo apt-get install libbz2-dev libreadline-dev libsqlite3-dev libffi-dev

如果还缺少依赖，完整列表如下：

sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

安装完这些补充的工具之后，再次执行：

pyenv install 3.7.3

就可以成功了，你可以不断的使用

pyenv versions

来查看被 pyenv 托管的 python 版本

而且你想装什么版本就装什么版本，想装几个装几个，都是完美共存，完美隔离，你可以在终端里输入

pyenv install

然后按下 tab 键，就可以看到所有可选的安装版本了

\* pyenv 安装很慢的解决办法：

可以先手动下载对应的版本压缩包，放到~/.pyenv/cache/下面，pyenv会校验md5值和完整性，确认无误的话就不会重新下载直接从这里安装

**使用刚才安装的 python 3.7.3**

首先我们需要明确一个概念，pyenv 和 pyenv-virtualenv 他们是如何协作的，你可以这么认为：

**pyenv 托管 python 版本，virtualenv 使用 python 版本**

好了，之前已经装好了版本，那么现在就来使用吧

**第 1 步：创建虚拟环境**

首先需要创建一个虚拟环境，执行命令：

pyenv virtualenv 3.7.3 venv

它的格式就是这样固定的，最后一个是你自己想要的环境的名字，可以随便取。稍等片刻，你将会看到：

***Looking in links: /tmp/tmpca63rmay***

***Requirement already satisfied: setuptools in /home/jeanphy/.pyenv/versions/3.7.3/envs/venv/lib/python3.7/site-packages (40.6.2)***

***Requirement already satisfied: pip in /home/jeanphy/.pyenv/versions/3.7.3/envs/venv/lib/python3.7/site-packages (18.1)***

类似于这样的回显信息，说明环境已经创建成功了，它还告诉了你，该虚拟环境的绝对路径，如果你进去看了，你就会发现，所谓的虚拟环境，就是把 python 装在 pyenv 的安装目录的某个文件夹中，以供它自己调用。

**第 2 步：激活虚拟环境**

在任意目录下，执行命令：

pyenv activate venv

pyenv deactivate(取消激活)

你会发现，在你的终端里面，多了一个类似于 (venv) 这样的一个东西，这时候你如果执行：

python --version

那就是 python 3.7.3 了

如果你执行：

pip --version

它会告诉你 pip 包安装的绝对路径，也是 pyenv 安装目录下的某个文件夹

如果你关掉了终端，那么下次启动你又得重新激活一次了，你可以使用如下命令：

首先 cd 到某一个目录，比如 ~/test

cd ~/test

然后在该目录下执行：

pyenv local my-env

你会发现已经被激活了，那么 local 命令和刚才有啥不同呢。如果你执行：

ls -al

你就会发现，在 ~/test 目录下，有个隐藏文件 .python-version，你可以看到这个文件里面，只写了一句话 my-env

这样你只要进入 ~/test 目录，就会自动激活虚拟环境

在虚拟环境下，你如果直接执行

python

就会进入到 python 的交互环境

如果你写了一个文件，名字叫做 app.py ，里面的内容只有一句代码：print(1)

然后执行：

python app.py

这时候，系统就会调用虚拟环境中的 python 解释器来执行这些代码了

**第 3 章：更新 pyenv**

由于我们是 git 克隆的，所以更新非常简单

cd ~/.pyenv 或者 cd $(pyenv root)

git pull

**第 4 章：卸载 pyenv**

由于 pyenv 把一切都放在 ~/.pyenv 下了，所以卸载很方便，两个步骤就行了

首先你需要删除环境变量

然后你需要执行：

rm -rf ~/.pyenv 或者 rm -rf $(pyenv root)



**删除虚拟环境**

pyenv uninstall venv # 删除 venv 这个虚拟环境

或

rm -rf ~/.pyenv/versions/venv/

**设置全局环境**

pyenv global 3.7.3 # 设置3.7.2为全局python环境

**为当前shell指定python版本**

pyenv shell 3.7.3

**取消当前shell的python版本**

unset PYENV_VERSION
