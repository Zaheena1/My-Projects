---
- name: Install Apache
  yum:
    name: httpd
    state: present

- name: Start Apache service
  service:
    name: httpd
    state: started
    enabled: true

- name: Copy index.html
  copy:
    src: index.html
    dest: /var/www/html/index.html
  notify: Restart Apache
