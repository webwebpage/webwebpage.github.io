# webpage for webweb

instructions on getting the site up:
- set your path gems path in bashrc/zshrc/etc:
    - `export GEM_HOME=$HOME/.gems`
        - note that:
            1. it's more standard to do $HOME/gems, I just hate unhidden library files
            2. the point of this is to avoid using sudo later
    - `export PATH=$PATH:$HOME/.gem/ruby/2.3.0/bin`
        - I copied this from the output from running the first command, for you it might be different
- install jekyll:
    - `gem install bundler jekyll`
- possibly run `bundler`
- run `bundle exec jekyll serve`

# instructions on regenerating the documentation:
- clone webweb into the root directory
- run `python examplify.py`
- presto!
