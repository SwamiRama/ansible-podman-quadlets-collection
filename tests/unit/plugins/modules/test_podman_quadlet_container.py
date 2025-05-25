---
- name: Test podman_quadlet_container module
  hosts: localhost
  gather_facts: no
  vars:
    test_container_name: test-nginx
    test_quadlet_dir: /tmp/test-quadlets
  
  tasks:
    - name: Create test directory
      ansible.builtin.file:
        path: "{{ test_quadlet_dir }}"
        state: directory
        mode: '0755'

    - name: Test creating a simple container
      community.podman_quadlets.podman_quadlet_container:
        name: "{{ test_container_name }}"
        image: docker.io/nginx:alpine
        state: present
        quadlet_dir: "{{ test_quadlet_dir }}"
      register: create_result

    - name: Verify container was created
      ansible.builtin.assert:
        that:
          - create_result.changed
          - create_result.quadlet_file == "{{ test_quadlet_dir }}/{{ test_container_name }}.container"

    - name: Verify quadlet file exists
      ansible.builtin.stat:
        path: "{{ create_result.quadlet_file }}"
      register: quadlet_file

    - name: Assert quadlet file was created
      ansible.builtin.assert:
        that:
          - quadlet_file.stat.exists
          - quadlet_file.stat.isreg

    - name: Read quadlet file content
      ansible.builtin.slurp:
        src: "{{ create_result.quadlet_file }}"
      register: quadlet_content

    - name: Verify quadlet content
      ansible.builtin.assert:
        that:
          - "'[Container]' in quadlet_content.content | b64decode"
          - "'Image=docker.io/nginx:alpine' in quadlet_content.content | b64decode"
          - "'ContainerName={{ test_container_name }}' in quadlet_content.content | b64decode"

    - name: Test idempotency - create same container again
      community.podman_quadlets.podman_quadlet_container:
        name: "{{ test_container_name }}"
        image: docker.io/nginx:alpine
        state: present
        quadlet_dir: "{{ test_quadlet_dir }}"
      register: idempotent_result

    - name: Verify idempotency
      ansible.builtin.assert:
        that:
          - not idempotent_result.changed

    - name: Test updating container with environment variables
      community.podman_quadlets.podman_quadlet_container:
        name: "{{ test_container_name }}"
        image: docker.io/nginx:alpine
        state: present
        environment:
          NGINX_PORT: "8080"
          DEBUG: "true"
        quadlet_dir: "{{ test_quadlet_dir }}"
      register: update_result

    - name: Verify update
      ansible.builtin.assert:
        that:
          - update_result.changed

    - name: Verify environment variables in quadlet
      ansible.builtin.slurp:
        src: "{{ update_result.quadlet_file }}"
      register: updated_content

    - name: Assert environment variables
      ansible.builtin.assert:
        that:
          - "'Environment=NGINX_PORT=8080' in updated_content.content | b64decode"
          - "'Environment=DEBUG=true' in updated_content.content | b64decode"

    - name: Test container with volumes and ports
      community.podman_quadlets.podman_quadlet_container:
        name: "{{ test_container_name }}-advanced"
        image: docker.io/nginx:alpine
        state: present
        volumes:
          - host_path: /tmp/nginx-data
            container_path: /usr/share/nginx/html
          - host_path: nginx-config.volume
            container_path: /etc/nginx/conf.d
        ports:
          - host_port: "8080"
            container_port: "80"
        networks:
          - test.network
        labels:
          app: nginx
          test: integration
        quadlet_dir: "{{ test_quadlet_dir }}"
      register: advanced_result

    - name: Verify advanced configuration
      ansible.builtin.slurp:
        src: "{{ advanced_result.quadlet_file }}"
      register: advanced_content

    - name: Assert advanced configuration
      ansible.builtin.assert:
        that:
          - "'Volume=/tmp/nginx-data:/usr/share/nginx/html' in advanced_content.content | b64decode"
          - "'Volume=nginx-config.volume:/etc/nginx/conf.d' in advanced_content.content | b64decode"
          - "'PublishPort=8080:80' in advanced_content.content | b64decode"
          - "'Network=test.network' in advanced_content.content | b64decode"
          - "'Label=app=nginx' in advanced_content.content | b64decode"

    - name: Test removing container
      community.podman_quadlets.podman_quadlet_container:
        name: "{{ test_container_name }}"
        state: absent
        quadlet_dir: "{{ test_quadlet_dir }}"
      register: remove_result

    - name: Verify removal
      ansible.builtin.assert:
        that:
          - remove_result.changed

    - name: Verify quadlet file was removed
      ansible.builtin.stat:
        path: "{{ test_quadlet_dir }}/{{ test_container_name }}.container"
      register: removed_file

    - name: Assert file was removed
      ansible.builtin.assert:
        that:
          - not removed_file.stat.exists

    - name: Test check mode
      community.podman_quadlets.podman_quadlet_container:
        name: "{{ test_container_name }}-checkmode"
        image: docker.io/nginx:alpine
        state: present
        quadlet_dir: "{{ test_quadlet_dir }}"
      check_mode: yes
      register: check_mode_result

    - name: Verify check mode
      ansible.builtin.assert:
        that:
          - check_mode_result.changed

    - name: Verify file was not created in check mode
      ansible.builtin.stat:
        path: "{{ test_quadlet_dir }}/{{ test_container_name }}-checkmode.container"
      register: check_mode_file

    - name: Assert file was not created
      ansible.builtin.assert:
        that:
          - not check_mode_file.stat.exists

  always:
    - name: Cleanup test directory
      ansible.builtin.file:
        path: "{{ test_quadlet_dir }}"
        state: absent