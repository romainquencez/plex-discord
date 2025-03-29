import os
from datetime import datetime

from discord_webhook import DiscordWebhook, DiscordEmbed
from plexapi.server import PlexServer
from dotenv import load_dotenv
import requests
from io import BytesIO

load_dotenv()

WEBHOOK_URL = os.environ["WEBHOOK_URL"]
PLEX_URL = os.environ["PLEX_URL"]
PLEX_TOKEN = os.environ["PLEX_TOKEN"]
FILENAME = "last_execution.txt"

def main():
    # plex
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)

    # read or create last update file
    try:
        with open(FILENAME, "r") as file:
            last_execution = int(file.readline())
    except FileNotFoundError:
        last_execution = None

    # get recently added medias
    medias = plex.library.recentlyAdded()
    for media in medias:
        added_at = int(media.addedAt.timestamp())

        # if media is older than last added date, skip it
        if last_execution is None or added_at < last_execution:
            break

        # initialize a new discord webhook
        webhook = DiscordWebhook(url=WEBHOOK_URL)

        title = f"{media.parentTitle} - {media.title}" if hasattr(media, "parentTitle") else media.title

        embed = DiscordEmbed(
            title=title,
            description=media.summary,
            color=media.ultraBlurColors.topLeft if media.ultraBlurColors else "EBAF00"
        )

        if media.year:
            embed.add_embed_field(name="Année de sortie", value=str(media.year))

        if media.audienceRating:
            embed.add_embed_field(name="Note des spectateurs", value=f"{media.audienceRating} / 10")

        if hasattr(media, "genres") and media.genres:
            embed.add_embed_field(name="Genres" if len(media.genres) > 1 else "Genre", value=", ".join([genre.tag for genre in media.genres]))

        if hasattr(media, "roles") and media.roles:
            embed.add_embed_field(name="Acteurs" if len(media.roles) > 1 else "Acteur", value=", ".join([role.tag for role in media.roles]))

        if hasattr(media, "directors") and media.directors:
            embed.add_embed_field(name="Réalisateurs" if len(media.directors) > 1 else "Réalisateur", value=", ".join([director.tag for director in media.directors]))

        webhook.add_embed(embed)

        webhook.content=f"Nouveau film ajouté sur Plex : https://app.plex.tv/desktop/#!/server/{plex.machineIdentifier}/details?key={media.key}"

        # thumbnail
        if media.thumbUrl:
            response = requests.get(media.thumbUrl)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                webhook.add_file(file=image_data, filename="thumb.jpg")
                embed.set_thumbnail(url="attachment://thumb.jpg")

        # send Discord message
        webhook.execute()

    # write last execution date
    with open(FILENAME, "w") as file:
        timestamp = int(datetime.now().timestamp())
        file.write(str(timestamp))

if __name__ == "__main__":
    main()
