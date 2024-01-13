Edit bashrc: nano ~/.bashrc
Reload bashrc: source ~/.bashrc

/*----- Store environment variables to pull in sensitive information in your flask app -----*/
export TWITCH_CLIENT_ID="<twitch app client_id"
export TWITCH_CLIENT_SECRET="<twitch app client secret>"
export TWITCH_BEARER_TOKEN="<twitch app OAuth token>"
export EVENTSUB_SECRET="<Your subscription secret>" # Change this to something better
export TWITCH_USER_ID="<twitch user_id / not username>"
/*----- End of environment variables -----*/
