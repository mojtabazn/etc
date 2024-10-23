# $HOME/.login* or similar files may first set $DEBUGINFOD_URLS.
# If $DEBUGINFOD_URLS is not set there, we set it from system *.url files.
# $HOME/.*rc or similar files may then amend $DEBUGINFOD_URLS.
# See also [man debuginfod-client-config] for other environment variables
# such as $DEBUGINFOD_MAXSIZE, $DEBUGINFOD_MAXTIME, $DEBUGINFOD_PROGRESS.

set prefix="/usr"
if (! $?DEBUGINFOD_URLS) then
    set DEBUGINFOD_URLS=`sh -c 'cat /dev/null "$0"/*.urls 2>/dev/null; :' "/etc/debuginfod" | tr '\n' ' '`
    if ( "$DEBUGINFOD_URLS" != "" ) then
        setenv DEBUGINFOD_URLS "$DEBUGINFOD_URLS"
    else
        unset DEBUGINFOD_URLS
    endif
    set DEBUGINFOD_IMA_CERT_PATH=`sh -c 'cat /dev/null "$0"/*.certpath 2>/dev/null; :' "/etc/debuginfod" | tr '\n' ':'`
    if ( "$DEBUGINFOD_IMA_CERT_PATH" != "" ) then
        setenv DEBUGINFOD_IMA_CERT_PATH "$DEBUGINFOD_IMA_CERT_PATH"
    else
        unset DEBUGINFOD_IMA_CERT_PATH
    endif
endif
unset prefix
