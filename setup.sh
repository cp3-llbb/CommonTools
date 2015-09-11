#!/bin/bash
# configure the origin repository
GITHUBUSERNAME=`git config user.github`
GITHUBUSERREMOTE=`git remote -v | grep upstream | awk '{print $2}' | head -n 1 | cut -d / -f 2`
git remote add origin git@github.com:${GITHUBUSERNAME}/${GITHUBUSERREMOTE}

# Add the remaining forks
git remote add OlivierBondu https://github.com/OlivierBondu/CommonTools.git
git remote add blinkseb https://github.com/blinkseb/CommonTools.git
# have not yet forked, but are expected to:
git remote add delaere https://github.com/delaere/CommonTools.git
git remote add BrieucF https://github.com/BrieucF/CommonTools.git
git remote add swertz https://github.com/swertz/CommonTools.git
git remote add vidalm https://github.com/vidalm/CommonTools.git
git remote add camillebeluffi https://github.com/camillebeluffi/CommonTools.git
git remote add acaudron https://github.com/acaudron/CommonTools.git
git remote add AlexandreMertens https://github.com/AlexandreMertens/CommonTools.git

