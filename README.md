# bow api

## 環境変数設定

デプロイするステージごとに `.env.{stage}`ファイルに以下の環境変数を定義する

| 環境変数         | 説明                                       |
| ---              | ---                                        |
| DOMAIN_NAME      | ドメイン名                                 |
| CERTIFICATE_NAME | 証明書のドメイン情報 (ex: `*.example.com`) |
| CERTIFICATE_ARN  | ACMに作成した証明書のARN                   |


