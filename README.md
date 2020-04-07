# -
具体结构：django+bootstrap
一下均为让我们的小伙伴更了解这个项目的结构。
强烈建议先看django官方文档
如有错误请及时更正

首先建立project，以此作为根目录，项目中文件夹名为mysite
然后在这个根目录下，有一个文件夹mysite，这包含了最基本的网站应用，还有一个manage.py文件，用于基本的项目操作，包括建立新应用，开启服务等

此时我们建立了bubbleworld这个application，这就是我们需要的网站应用，根目录下出现了同名文件夹，现在讲解该文件夹内部结构。
migrations 在数据库迁移之后的产物，一般在application写好之后初始化产生
templates html网页模板，应用了bootstrap里的模板，用于实现基本的网页页面，如登陆，主页，帖子页面，评论页面等
models.py 需要建立相关的类和方法（独立于类之外），存储于数据库之中，相关操作被django封装，所以需要建立user，post，comment之类的model用于指导django存储数据
admin.py 在其中register models.py中的相关model，无需特别操作
form.py 表单类的建立，用于指导数据的导入
middle.py 中间件，用于实现特殊操作，你可以把其他地方不合适的方法放于此处
tests.py 系统自动生成，暂无作用
views.py 实现前后端之间的直接信息交换，包括类与方法
urls.py 此处需注意，在mysite子文件中也有一个同名文件用来实现最基本的网址转换，来导向到对应的application，再由该application的urls文件实现复杂功能的网址关联。再说到此文件作用，用于实现网址与功能的关联，即urls与views文件的关联

接下来说明html的实现
用bootstrap构建相应模板，将对应功能与urls关联，实现前后端的关联，该部分需要查阅资料，也可以参考GitHub中其他的项目
