#
# Get container pid and create net namespace
# input container name/id and create associated netns
# First create a net namespace in /var/run/netns
cn=$1
cnpid=$(docker inspect $cn | grep '"Pid"' | awk '{ print $2 }' | sed 's/,.*//' )
echo "Now create netns ${cn} based on Pid=${cnpid}"
touch /var/run/netns/${cn}
echo "ln -sf /proc/${cnpid}/ns/net /var/run/netns/${cn}"
ln -sf /proc/$cnpid/ns/net /var/run/netns/$cn
#
