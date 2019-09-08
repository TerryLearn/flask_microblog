### flask_microblog
learn flask again
![链接地址](https://juejin.im/entry/5af569076fb9a07aa34a5077)
#### 数据库
 * 第一个是Flask-SQLAlchemy，这个插件为流行的SQLAlchemy包做了一层封装以便在Flask中调用更方便，
 类似SQLAlchemy这样的包叫做Object Relational Mapper，简称ORM。 ORM允许应用程序使用高级实体（如类，对象和方法）而不是表和SQL来管理数据库。 ORM的工作就是将高级操作转换成数据库命令。
 
 * SQLAlchemy不只是某一款数据库软件的ORM，而是支持包含MySQL、PostgreSQL和SQLite在内的很多数据库软件。简直是太强大了，你可以在开发的时候使用简单易用且无需另起服务的SQLite，需要部署应用到生产服务器上时，则选用更健壮的MySQL或PostgreSQL服务，并且不需要修改应用代码（译者注：只需修改应用配置
 
*  我将在本章中介绍的第二个插件是Flask-Migrate。 这个插件是Alembic的一个Flask封装，是SQLAlchemy的一个数据库迁移框架。 使用数据库迁移增加了启动数据库时候的一些工作，但这对将来的数据库结构稳健变更来说，是一个很小的代价。

##### 数据库迁移
* Flask-Migrate通过flask命令暴露来它的子命令。 你已经看过flask run，这是一个Flask本身的子命令。 Flask-Migrate添加了flask db子命令来管理与数据库迁移相关的所有事情。 那么让我们通过运行flask db init来创建microblog的迁移存储库
 
 * 包含映射到User数据库模型的用户表的迁移存储库生成后，是时候创建第一次数据库迁移了。 有两种方法来创建数据库迁移：手动或自动。 要自动生成迁移，Alembic会将数据库模型定义的数据库模式与数据库中当前使用的实际数据库模式进行比较。 然后，使用必要的更改来填充迁移脚本，以使数据库模式与应用程序模型匹配。 当前情况是，由于之前没有数据库，自动迁移将把整个User模型添加到迁移脚本中。 flask db migrate子命令生成这些自动迁移
 ```
 (venv) $ flask db migrate -m "users table"
 INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
 INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
 INFO  [alembic.autogenerate.compare] Detected added table 'user'
 INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_email' on '['email']'
 INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_username' on '['username'] 
 
```
* 通过命令输出，你可以了解到Alembic在创建迁移的过程中执行了哪些逻辑。前两行是常规信息，通常可以忽略。 之后的输出表明检测到了一个用户表和两个索引。 然后它会告诉你迁移脚本的输出路径。 e517276bb1c2是自动生成的一个用于迁移的唯一标识（你运行的结果会有所不同）。 -m可选参数为迁移添加了一个简短的注释。

* 生成的迁移脚本现在是你项目的一部分了，需要将其合并到源代码管理中。 如果你好奇，并检查了它的代码，就会发现它有两个函数叫upgrade()和downgrade()。 upgrade()函数应用迁移，downgrade()函数回滚迁移。 Alembic通过使用降级方法可以将数据库迁移到历史中的任何点，甚至迁移到较旧的版本
* flask db migrate命令不会对数据库进行任何更改，只会生成迁移脚本。 要将更改应用到数据库，必须使用flask db upgrade命令。
##### 数据库升级和降级
* 通过数据库迁移机制的支持，在你修改应用中的模型之后，将生成一个新的迁移脚本（flask db migrate），你可能会审查它以确保自动生成的正确性，然后将更改应用到你的开发数据库（flask db upgrade）。 测试无误后，将迁移脚本添加到源代码管理并提交。

* 当准备将新版本的应用发布到生产服务器时，你只需要获取包含新增迁移脚本的更新版本的应用，然后运行flask db upgrade即可。 Alembic将检测到生产数据库未更新到最新版本，并运行在上一版本之后创建的所有新增迁移脚本。
* flask db downgrade命令可以回滚上次的迁移。 虽然在生产系统上不太可能需要此选项，但在开发过程中可能会发现它非常有用。 你可能已经生成了一个迁移脚本并将其应用，只是发现所做的更改并不完全是你所需要的。 在这种情况下，可以降级数据库，删除迁移脚本，然后生成一个新的来替换它


##### 数据库使用

* 对数据库的更改是在会话的上下文中完成的，你可以通过db.session进行访问验证。 允许在会话中累积多个更改，一旦所有更改都被注册，你可以发出一个指令db.session.commit()来以原子方式写入所有更改。 如果在会话执行的任何时候出现错误，调用db.session.rollback()会中止会话并删除存储在其中的所有更改。 要记住的重要一点是，只有在调用db.session.commit()时才会将更改写入数据库。 会话可以保证数据库永远不会处于不一致的状态

* 所有模型都有一个query属性，它是运行数据库查询的入口。 最基本的查询就是返回该类的所有元素，它被适当地命名为all()。 请注意，添加这些用户时，它们的id字段依次自动设置为1和2。

    另外一种查询方式是，如果你知道用户的id，可以用以下方式直接获取用户实例：
    ```
    >>> u = User.query.get(1)
    >>> u
    <User john>
    
    
    >>> # print post author and body for all posts 
    >>> posts = Post.query.all()
    >>> for p in posts:
    ...     print(p.id, p.author.username, p.body)
    ...
    1 john my first post!
    
    # get all users in reverse alphabetical order
    >>> User.query.order_by(User.username.desc()).all()
    [<User susan>, <User john>]
    
    >>> users = User.query.all()
    >>> for u in users:
    ...     db.session.delete(u)
    ...
    >>> posts = Post.query.all()
    >>> for p in posts:
    ...     db.session.delete(p)
    ...
    >>> db.session.commit()
   ```
   
   ##### falsk shell
  *  flask shell命令是flask命令集中的另一个非常有用的工具。 shell命令是Flask在继run之后的实现第二个“核心”命令。 这个命令的目的是在应用的上下文中启动一个Python解释器
   * !(lask-sqlalchemy链接)[https://flask-sqlalchemy.palletsprojects.com/en/2.x/]
   
  * 使用常规的解释器会话时，除非明确地被导入，否则app对象是未知的，但是当使用flask shell时，该命令预先导入应用实例。 flask shell的绝妙之处不在于它预先导入了app，而是你可以配置一个“shell上下文”，也就是可以预先导入一份对象列表。
   
   在microblog.py中实现一个函数，它通过添加数据库实例和模型来创建了一个shell上下文环境：
   ```
   from app import app, db
   from app.models import User, Post
   
   @app.shell_context_processor
   def make_shell_context():
   return {'db': db, 'User': User, 'Post': Post}
   ```


###### Flask-Login

Flask-Login插件需要在用户模型上实现某些属性和方法。这种做法很棒，因为只要将这些必需项添加到模型中，Flask-Login就没有其他依赖了，它就可以与基于任何数据库系统的用户模型一起工作。

必须的四项如下：

* is_authenticated: 一个用来表示用户是否通过登录认证的属性，用True和False表示。
* is_active: 如果用户账户是活跃的，那么这个属性是True，否则就是False（译者注：活跃用户的定义是该用户的登录状态是否通过用户名密码登录，通过“记住我”功能保持登录状态的用户是非活跃的）。
* is_anonymous: 常规用户的该属性是False，对特定的匿名用户是True。
* get_id(): 返回用户的唯一id的方法，返回值类型是字符串(Python 2下返回unicode字符串).
我可以很容易地实现这四个属性或方法，但是由于它们是相当通用的，因此Flask-Login提供了一个叫做UserMixin的mixin类来将它们归纳其中.
