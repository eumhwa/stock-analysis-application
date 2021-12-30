# Manifest 파일 설명
## docker-compose setting
1. docker network 설정
    - docker-compose 내 서비스 통신을 위한 static ip 부여를 위한 docker network 생성
        ```
        $ docker network create --gateway 172.26.0.1 --subnet 172.26.0.0/16 stock-project
        $ docker network ls
        ```
2. docker image 빌드
    - local_build.sh 실행
        ```
        $ sh ./local_build.sh
        ```
3. docker-compose로 서비스 실행
    - docker-compose.yml 내 네트워크 설정 확인!
    - volume mount 경로 확인!
        ```
        $ docker-compose up -d
        ```

## minikube setting
1. minikue 실행
    - minikube 실행
        ```
        $ minikube start
        ```
2. docker image 빌드
    - minikube_build.sh 실행
        ```
        $ sh ./minikube_build.sh
        ```
3. TBD