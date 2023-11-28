#!/bin/bash -norc
docker run -d -t -p 40080:80 -v /home/r-oguro/repository/git:/repository/git --env-file ~/.openai_api_key.sh --privileged --name openai_jupyter_p310 r-oguro/openai_jupyter_p310:test
