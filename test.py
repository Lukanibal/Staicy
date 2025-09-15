

            
















































async def split_string(text, chunk_size=1500):
    # Create a list to hold the chunks
    chunks = []
    
    # Loop through the text and create chunks
    for i in range(0, len(text), chunk_size):
        await chunks.append(text[i:i + chunk_size])
    
    return chunks











