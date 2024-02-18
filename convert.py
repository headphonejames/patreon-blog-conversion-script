import json
import os
import markdownify
import shutil
import glob

legal_img_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']

def create_img_mapping_obj(json_file, img_mapping_obj):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for post in data['included']:
            attributes = post['attributes']
            # check what is in the attributes
            if 'file_name' in attributes:
                id = post['id']
                img_file = attributes['file_name']
                img_file_extension = img_file.split('.')[-1]
                if img_file_extension in legal_img_extensions:
                    img_mapping_obj[id] = {"ext": img_file_extension}

def convert_json_to_md(json_file, img_mapping_obj):
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for post in data['data']:
            attributes = post['attributes']
            title = attributes.get('title', 'Untitled')
            published_at = attributes.get('published_at', 'No Date')
            teaser_text = attributes.get('teaser_text', '\"\"')
            if not teaser_text:
                teaser_text = '\"\"'
            else:
                # limit teaser_text to one line - strip after a newline
                teaser_text = teaser_text.split('\n')[0]

            content = attributes.get('content', '\"\"')

            md_content = f"---\n"
            md_content += f"title: {title}\n"
            md_content += f"description: {teaser_text}\n"
            md_content += f"intro: {teaser_text}\n"
            md_content += f"style:\n"
            md_content += f"  template: split\n"
            md_content += f"  card_template: grid\n"
            md_content += f"  hero_template: image\n"
            md_content += f"  hero_image_opacity: \"\"\n"
            md_content += f"  container: md\n"
            md_content += f"pubDate: {published_at}\n"
            if 'relationships' in post and 'images' in post['relationships'] and 'data' in post['relationships']['images'] and post['relationships']['images']['data'] and 'id' in post['relationships']['images']['data'][0]:
                img_id = post['relationships']['images']['data'][0]['id']
                if img_id in img_mapping_obj:
                    md_content += f"thumbnail: /src/assets/{img_id}.{img_mapping_obj[img_id]['ext']}\n"
                else:
                    md_content += f"thumbnail: \"\"\n"
            else:
                md_content += f"thumbnail: \"\"\n"x

            md_content += f"---\n\n"

            # strip out NBSP characters from the content
            content = content.replace(u'\xa0', u' ')

            md_content += markdownify.markdownify(content, heading_style="ATX")

            # Create a valid filename
            filename = f"{title.replace(' ', '_').replace('/', '_')}.mdx"
            filepath = os.path.join(output_dir, filename)

            # Write to Markdown file
            with open(filepath, 'w', encoding='utf-8') as md_file:
                md_file.write(md_content)
            print(f"Generated Markdown for {title}")

        for post in data['included']:
            attributes = post['attributes']
            # check what is in the attributes
            if 'file_name' in attributes:
                # its an image, move it with the first name as the id
                img_file = attributes['file_name']
                img_id = post['id']
#                 print(json.dumps(post, indent=2))
#                 print(json.dumps(img_mapping_obj, indent=2))

                img_file_extension = img_file.split('.')[-1]
                # use python to copy the file from the source to the destination
                # Use glob to find files matching the pattern
                pattern = f"{source_dir}/*{img_id}_*.{img_file_extension}"
                matching_files = glob.glob(pattern)

                # Copy each matching file
                for file_path in matching_files:
                    # check if the file exists already
                    if not os.path.exists(f'{image_dir}/{img_id}.{img_file_extension}'):
                        print(f"Copying {file_path} to {image_dir}/{img_id}.{img_file_extension}")
                        # copy the original name
                        shutil.copy(f'{file_path}', f'{image_dir}/')
                        # copy renamed using id as filename
                        shutil.copy(f'{file_path}', f'{image_dir}/{img_id}.{img_file_extension}')

def process_all_json_files():
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # First build image mapping object
    for file in os.listdir(source_dir):
        if file.endswith('.json'):
            json_file_path = os.path.join(source_dir, file)
            create_img_mapping_obj(json_file_path, img_mapping_obj)


    for file in os.listdir(source_dir):
        if file.endswith('.json'):
            json_file_path = os.path.join(source_dir, file)
            convert_json_to_md(json_file_path, img_mapping_obj)
    print("All JSON files have been processed.")

# Set your source and output directories
img_mapping_obj = {}
current_dir = os.path.dirname(os.path.realpath(__file__))
source_dir = f'{current_dir}/downloads'  # Update this path to your source directory
output_dir = f'{current_dir}/converted_md_files'  # Update this path to your output directory
image_dir = f'{current_dir}/images'
# Convert all JSON files in the source directory to Markdown
process_all_json_files()
