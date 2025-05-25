Examples
========

This section provides practical examples for common deployment scenarios.

Single Container Deployments
----------------------------

Basic Web Server
~~~~~~~~~~~~~~~~

Deploy a simple nginx web server::

    ---
    - name: Deploy nginx
      hosts: localhost
      tasks:
        - name: Create nginx container
          community.podman_quadlets.podman_quadlet_container:
            name: webserver
            image: docker.io/nginx:alpine
            ports:
              - host_port: "8080"
                container_port: "80"
            volumes:
              - host_path: ./html
                container_path: /usr/share/nginx/html
            labels:
              app: webserver
              env: production

Container with Secrets
~~~~~~~~~~~~~~~~~~~~~~

Deploy a container using secrets for sensitive data::

    ---
    - name: Deploy app with secrets
      hosts: localhost
      tasks:
        - name: Create database password
          community.podman_quadlets.podman_quadlet_secret:
            name: db-password
            data: "{{ vault_db_password }}"
        
        - name: Create application
          community.podman_quadlets.podman_quadlet_container:
            name: myapp
            image: myapp:latest
            secrets:
              db-password: DATABASE_PASSWORD
            environment:
              DATABASE_HOST: localhost
              DATABASE_NAME: myapp

Multi-Container Applications
----------------------------

WordPress with MariaDB
~~~~~~~~~~~~~~~~~~~~~~

Deploy a complete WordPress stack::

    ---
    - name: Deploy WordPress
      hosts: container_hosts
      vars:
        project_name: wordpress
        containers:
          - name: wordpress-db.container
            container_image: docker.io/mariadb:11
            container_name: wordpress-db
            environment_variables:
              MARIADB_ROOT_PASSWORD: "{{ vault_root_pass }}"
              MARIADB_DATABASE: wordpress
              MARIADB_USER: wordpress
              MARIADB_PASSWORD: "{{ vault_db_pass }}"
            volumes:
              - host_path: wordpress-db.volume
                container_path: /var/lib/mysql
            networks:
              - wordpress.network
          
          - name: wordpress.container
            container_image: docker.io/wordpress:latest
            container_name: wordpress
            required_services: wordpress-db.service
            after_services: wordpress-db.service
            environment_variables:
              WORDPRESS_DB_HOST: wordpress-db
              WORDPRESS_DB_USER: wordpress
              WORDPRESS_DB_PASSWORD: "{{ vault_db_pass }}"
            ports:
              - host_port: "8080"
                container_port: "80"
            volumes:
              - host_path: wordpress-data.volume
                container_path: /var/www/html
            networks:
              - wordpress.network
      roles:
        - community.podman_quadlets.podman_quadlets

Microservices Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy a microservices application with service discovery::

    ---
    - name: Deploy microservices
      hosts: container_hosts
      vars:
        project_name: microservices
        containers:
          # API Gateway
          - name: gateway.container
            container_image: nginx:alpine
            container_name: gateway
            ports:
              - host_port: "80"
                container_port: "80"
            volumes:
              - host_path: ./nginx.conf
                container_path: /etc/nginx/nginx.conf
            networks:
              - services.network
          
          # User Service
          - name: user-service.container
            container_image: myapp/user-service:latest
            container_name: user-service
            environment_variables:
              SERVICE_PORT: "8001"
              DB_CONNECTION: "{{ vault_user_db }}"
            networks:
              - services.network
              - database.network
          
          # Order Service
          - name: order-service.container
            container_image: myapp/order-service:latest
            container_name: order-service
            environment_variables:
              SERVICE_PORT: "8002"
              DB_CONNECTION: "{{ vault_order_db }}"
            networks:
              - services.network
              - database.network
          
          # Cache Service
          - name: redis.container
            container_image: redis:alpine
            container_name: redis
            networks:
              - services.network
      roles:
        - community.podman_quadlets.podman_quadlets

Advanced Configurations
-----------------------

Container with Health Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy a container with comprehensive health monitoring::

    ---
    - name: Deploy monitored application
      hosts: localhost
      tasks:
        - name: Create application with health checks
          community.podman_quadlets.podman_quadlet_container:
            name: webapp
            image: myapp:latest
            health_cmd: "/healthcheck.sh"
            health_interval: "30s"
            health_timeout: "3s"
            health_retries: 3
            health_start_period: "40s"
            restart_policy: "on-failure"
            environment:
              HEALTH_CHECK_ENDPOINT: "/health"

Using Custom Networks
~~~~~~~~~~~~~~~~~~~~~

Create isolated networks for your containers::

    ---
    - name: Setup custom networking
      hosts: localhost
      tasks:
        - name: Create internal network
          community.podman_quadlets.podman_quadlet_network:
            name: backend
            internal: true
            subnet: 172.20.0.0/16
            gateway: 172.20.0.1
        
        - name: Create DMZ network
          community.podman_quadlets.podman_quadlet_network:
            name: dmz
            subnet: 172.21.0.0/16
            labels:
              zone: dmz
              security: high

Persistent Storage
~~~~~~~~~~~~~~~~~~

Configure volumes for persistent data::

    ---
    - name: Setup persistent storage
      hosts: localhost
      tasks:
        - name: Create data volume
          community.podman_quadlets.podman_quadlet_volume:
            name: app-data
            driver: local
            labels:
              backup: daily
              retention: 30d
        
        - name: Create NFS volume
          community.podman_quadlets.podman_quadlet_volume:
            name: shared-data
            driver: local
            options:
              type: nfs
              o: "addr=nfs.example.com,rw"
              device: ":/exports/data"

Best Practices
--------------

1. **Use Secrets for Sensitive Data**
   
   Never hardcode passwords or API keys in your playbooks.

2. **Define Dependencies**
   
   Use `required_services` and `after_services` to ensure proper startup order.

3. **Implement Health Checks**
   
   Add health checks to ensure containers are functioning properly.

4. **Use Named Volumes**
   
   Prefer named volumes over bind mounts for better portability.

5. **Label Everything**
   
   Use labels for organization and to enable tooling integration.