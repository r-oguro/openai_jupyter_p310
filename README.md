# openai_jupyter_p310
For sample emvironment of openai api and jupyter notebook

docker内にopenaiのAPIの実行環境と、それを利用するjupyter notebookのサンプルを持つコンテナを作成する。
dockerのイメージ作成はdocker_build.shを実行し、コンテナの起動はstart_container.shを実行する。
server.pyは、ポート40080で待ち受けるwebアプリのサンプル。コンテナ内では、80番のポートで待ち受けている。
