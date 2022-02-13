Custom homeassistant integration for Halo Infinite ranked playlists. Lets the user see they're rank in HA along with recent statistics like K/D and damage.

Relies on the halo-infinite API on autocode.gg, so you'll need an API token from there. Default polling rate is once every 5 minutes. Two api calls
are needed for each poll, so this will use ~17,300 of your free api rate per month.

Once added to config/custom_components, you can use the following in confuration.yaml:

sensor:  
&nbsp;&nbsp;api_key: <api_token>  
&nbsp;&nbsp;gamer_tag: <gamer_tag>  
&nbsp;&nbsp;ranked_inputs:  
&nbsp;&nbsp;&nbsp;&nbsp;- crossplay  
&nbsp;&nbsp;&nbsp;&nbsp;- controller  
&nbsp;&nbsp;&nbsp;&nbsp;- mnk  
        
Playlist options may be excluded from the configuration.  
  
