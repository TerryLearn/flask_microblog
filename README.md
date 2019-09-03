### flask_microblog
learn flask again

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



