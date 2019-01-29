python3 regenerate
bundle exec jekyll build
cd _site
git add .
export WEBWEBPAGE_COMMIT_MESSAGE_DATE_STRING=$(date)
git commit -m "$date - update"
git push -f
cd ..
