FROM websphere-liberty:20.0.0.6-full-java8-ibmjava

ENV SERVERDIRNAME reviews

# Copiar archivos de configuración
COPY ./servers/LibertyProjectServer /opt/ibm/wlp/usr/servers/defaultServer/

# Copiar el WAR compilado a la carpeta de la aplicación
COPY ./reviews-application/build/libs/reviews-application-1.0.war /opt/ibm/wlp/usr/servers/defaultServer/apps/

RUN /opt/ibm/wlp/bin/installUtility install  --acceptLicense /opt/ibm/wlp/usr/servers/defaultServer/server.xml && \
    chmod -R g=rwx /opt/ibm/wlp/output/defaultServer/

ARG service_version
ARG enable_ratings
ARG star_color
ARG ratings_hostname
ENV SERVICE_VERSION ${service_version:-v1}
ENV ENABLE_RATINGS ${enable_ratings:-false}
ENV STAR_COLOR ${star_color:-black}
ENV RATINGS_HOSTNAME ${ratings_hostname:-ratings}

EXPOSE 9080

CMD ["/opt/ibm/wlp/bin/server", "run", "defaultServer"]