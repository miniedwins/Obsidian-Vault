首先建立本地端的 `RSA` 金鑰

~~~shell
ssh-keygen -t rsa -b 4096 -C "your e-mail"
~~~  

拷貝公鑰內容 (注意 : 不要複製到私鑰的內)

```shell
cd ~/.ssh
cat id_rsa.pub
```

進入到 Github Settings -> SSH and GPG keys -> Add New SSH key 即可將本地端程式碼推送到 Repositories

![[github_keys_setting.png]]