import os
import zipfile
import shutil


def create_debian_package(ipa_file):
    # Get the IPA filename without extension
    package_name = os.path.splitext(os.path.basename(ipa_file))[0]

    # Create Builds directory if it doesn't exist
    builds_dir = "Builds"
    if not os.path.exists(builds_dir):
        os.makedirs(builds_dir)

    # Create package directory inside Builds
    package_dir = os.path.join(builds_dir, package_name)
    debian_dir = os.path.join(package_dir, "DEBIAN")
    app_dir = os.path.join(package_dir, "Application")

    # Create directories if they don't exist
    if not os.path.exists(debian_dir):
        os.makedirs(debian_dir)
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

    # Get user details
    print("Please enter the following details:")
    app_name = input("Package: ")
    version = input("Version: ")

    # Platform selection
    while True:
        platform = input("Platform (ios/tvos): ").lower()
        if platform == "ios":
            architecture = "iphoneos-arm64"
            break
        elif platform == "tvos":
            architecture = "appletvos-arm64"
            break
        else:
            print("Invalid platform. Please enter 'ios' or 'tvos'")

    maintainer = input("Maintainer: ")
    description = input("Description: ")
    section = "utils"

    # Create a temporary directory for extraction
    temp_dir = os.path.join(builds_dir, "temp_extract")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # Extract IPA file
    with zipfile.ZipFile(ipa_file, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Find the .app directory in Payload folder
    payload_dir = os.path.join(temp_dir, "Payload")
    app_folder = None
    for item in os.listdir(payload_dir):
        if item.endswith(".app"):
            app_folder = item
            break

    if app_folder:
        # Get the app name without .app extension
        app_name_without_ext = os.path.splitext(app_folder)[0]
        source_app_path = os.path.join(payload_dir, app_folder)

        # Append .app to the app folder name
        destination_app_path = os.path.join(app_dir, app_name_without_ext + ".app")
        shutil.copytree(source_app_path, destination_app_path)

    # Clean up temporary directory
    shutil.rmtree(temp_dir)

    # Create control file in DEBIAN directory
    control_content = f"""Package: {app_name}
Version: {version}
Architecture: {architecture}
Maintainer: {maintainer}
Description: {description}
Section: {section}
"""
    control_file_path = os.path.join(debian_dir, "control")
    with open(control_file_path, "w") as control_file:
        control_file.write(control_content)

    # Create the .deb package using dpkg-deb
    deb_file_name = f"{package_name}.deb"
    deb_path = os.path.join(builds_dir, deb_file_name)
    os.system(f"dpkg-deb --build {package_dir} {deb_path}")

    print(f"DEB package created successfully in {deb_path}!")
    print(f"Build files are preserved in {package_dir}")


# Example usage
ipa_file_path = input("Enter the path to the IPA file: ")
create_debian_package(ipa_file_path)
