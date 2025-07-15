# 又拍云自动更新边缘规则重定向端口
这个脚本是搭配lucky+又拍云重定向来使用的，详情请看[https://www.ytca.top/stun/2193/](https://www.ytca.top/stun/2193/)  
有两个版本，python版本和shell版本的，效果都一样  
iStoreOS不能使用shell版本，jq库版本太老了，不兼容  
# 快速开始
1. 先在redirect.py/sh文件内将账户信息填好
- USERNAME = "又拍云账户"
- PASSWORD = "又拍云密码"
- BUCKET_NAME = "服务名称"  
其他的保持默认即可

2. 运行脚本
python使用```python ./redirect.py -p 新端口```来进行端口号的修改  
shell使用```./redirect.sh -p 新端口```来进行端口号的修改

请确保已经创建了边缘规则重定向1和重定向2

# 实现原理
1. 登入又拍云账户获取到cookie
2. 获取边缘规则配置信息
3. 修改后上传覆盖原来的边缘规则配置

# 运行
```python ./rewrite.py -p 端口号```
# 运行结果
```
[1] 正在登录...
[√] 登录成功，cookie 获取成功
[2] 正在获取 Bucket 配置...
[3] 正在处理规则...
[→] 匹配规则：重定向1（ID: 1609001）
[√] 规则 "重定向1" 修改成功
[→] 匹配规则：重定向2（ID: 1609002）
[√] 规则 "重定向2" 修改成功
[完成] 所有规则处理完毕。
```

# 与lucky搭配利用方式
在lucky的stun设置一个自定义脚本，当stun的端口或端口号发生变化的时候会自动执行该脚本
```python ./redirect.py -p ${port}```
