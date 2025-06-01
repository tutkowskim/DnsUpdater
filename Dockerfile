FROM eclipse-temurin:21-jdk AS build
WORKDIR /app
COPY . /app
RUN ./gradlew --no-daemon clean installDist

FROM eclipse-temurin:21-jdk AS runtime
WORKDIR /app
COPY --from=build /app/build/install/DnsUpdater /app
RUN chmod +x ./bin/DnsUpdater

ENTRYPOINT ["sh", "./bin/DnsUpdater"]