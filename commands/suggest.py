if message.content.startswith(".suggest"):
        channel_entry = 1016869552707084378
        y = message.content
        z = y.replace(".suggest", "", 1)
        channel = client.get_channel(channel_entry) 
        await channel.send(f"from:`{message.author}`, suggestion: {z}")
