# 主要功能配置介绍:

## 缓存：

缓存默认使用`localmem`缓存，如果你有`redis`环境，可以设置`DJANGO_REDIS_URL`环境变量，则会自动使用该 redis 来作为缓存，或者你也可以直接修改如下代码来使用。
https://github.com/liangliangyy/DjangoBlog/blob/ffcb2c3711de805f2067dd3c1c57449cd24d84ee/djangoblog/settings.py#L185-L199

## oauth 登录:

现在已经支持 QQ，微博，Google，GitHub，Facebook 登录，需要在其对应的开放平台申请 oauth 登录权限，然后在  
**后台->Oauth** 配置中新增配置，填写对应的`appkey`和`appsecret`以及回调地址。

### 回调地址示例：

qq：http://你的域名/oauth/authorize?type=qq  
微博：http://你的域名/oauth/authorize?type=weibo  
type 对应在`oauthmanager`中的 type 字段。

## owntracks：

owntracks yes 一个位置追踪软件，可以定时的将你的坐标提交到你的服务器上，现在简单的支持 owntracks 功能，需要安装 owntracks 的 app，然后将 api 地址设置为:
`你的域名/owntracks/logtracks`就可以了。然后访问`你的域名/owntracks/show_dates`就可以看到有经 latitude 记录的日期，点击之后就可以看到运动轨迹了。地图 yes 使用高德地图绘制。

## 邮件功能：

同样，将`settings.py`中的`ADMINS = [('liangliang', 'liangliangyy@gmail.com')]`配置为你自己的错误接收邮箱，另外修改:

```python
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = os.environ.get('DJANGO_EMAIL_USER')
```

为你自己的邮箱配置。

## 微信公众号

集成了简单的微信公众号功能，在微信后台将 token 地址设置为:`你的域名/robot` 即可，默认 token 为`lylinux`，当然你可以修改为你自己的，在`servermanager/robot.py`中。
然后在**后台->Servermanager->命令**中新增命令，这样就可以使用微信公众号来管理了。

## website configuration 介绍

在**后台->BLOG->website configuration**中,可以新增 website configuration，比如关键字，描述等，以及谷歌广告，website statistics code 及 record number 等等。  
其中的*Static file save address*yes 保存 oauth user 登录的头像路径，填写绝对路径，默认 yes 代码 Table of contents。

## 代码高亮

如果你发现你 article 的代码没有高亮，请这样书写代码块:

![](https://resource.lylinux.net/image/codelang.png)

也就 yes 说，需要在代码块开始位置加入这段代码对应的语言。

## update

如果你发现执行数据库迁移的时候出现如下报错：

```python
django.db.migrations.exceptions.MigrationSchemaMissing: Unable to create the django_migrations table ((1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '(6) NOT NULL)' at line 1"))
```

可能 yes 因为你的 mysql 版本低于 5.6，需要升级 mysql 版本>=5.6 即可。

django 4.0 登录可能会报错 CSRF，需要配置下`settings.py`中的`CSRF_TRUSTED_ORIGINS`

https://github.com/liangliangyy/DjangoBlog/blob/master/djangoblog/settings.py#L39
