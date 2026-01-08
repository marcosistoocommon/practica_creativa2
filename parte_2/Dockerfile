FROM python:3.9-slim

WORKDIR /app

COPY bookinfo/src/productpage/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bookinfo/src/productpage/ ./

EXPOSE 8080

RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'TEAM_ID=${TEAM_ID:-17}' >> /entrypoint.sh && \
    echo 'APP_OWNER=${APP_OWNER:-owner-et-al}' >> /entrypoint.sh && \
    echo 'sed -i "s|{{TEAM_ID}}|$TEAM_ID|g; s|{{APP_OWNER}}|$APP_OWNER|g" templates/productpage.html' >> /entrypoint.sh && \
    echo 'exec python3 productpage_monolith.py 8080' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]