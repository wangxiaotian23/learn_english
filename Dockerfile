FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html day1.html day2.html day3.html day4.html day5.html day6.html day7.html /usr/share/nginx/html/
COPY ielts/*.html ielts/*.json /usr/share/nginx/html/ielts/
COPY ielts/sentences/ /usr/share/nginx/html/ielts/sentences/
COPY ielts/wordlists/ /usr/share/nginx/html/ielts/wordlists/

EXPOSE 80
