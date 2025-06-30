import os
import zipfile


def zip_sessions(session_dir='sessions', output_zip='sessions.zip'):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for filename in os.listdir(session_dir):
            if filename.endswith('.session'):
                filepath = os.path.join(session_dir, filename)
                zipf.write(filepath, arcname=filename)
    return output_zip
