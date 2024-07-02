import pathlib
import subprocess  # noqa: S404

PROJECT_DIR = pathlib.Path(__file__).parent.parent.parent
PROJECT_DIR_NAME = PROJECT_DIR.name

DEFAULT_PROJECT_DIR = "aiogram-bot-template"
DEFAULT_APP_FOLDER_NAME = "aiogram_bot_template"


def get_app_name(project_dir_name: str) -> str:
    suggested_app_name = project_dir_name.replace("-", "_")
    print(f"Suggested app name: [{suggested_app_name}]")  # noqa: T201
    if get_confirmation("Accept?", default_option=True):
        return suggested_app_name
    return input("Input app name: ")


def capitalize_app_name(app_name: str) -> list[str]:
    words = app_name.replace("_", " ").split()
    return [x.capitalize() for x in words]


def get_confirmation(question: str, default_option: bool | None) -> bool:
    input_prompt = "{question} (Y/y/N/n){default_option_possible}: ".format(
        question=question,
        default_option_possible=(
            " (default={default_option})".format(
                default_option="Y" if default_option else "N",
            )
            if default_option is not None
            else ""
        ),
    )
    while True:
        user_answer = input(input_prompt)
        if user_answer.lower() == "y":
            return True
        if user_answer.lower() == "n":
            return False
        if default_option is not None and not user_answer:
            return default_option
        print("Wrong input")  # noqa: T201


def rename_app_folder(
    *,
    project_dir: pathlib.Path,
    old_folder_name: str,
    new_folder_name: str,
) -> None:

    old_folder = project_dir / old_folder_name
    new_folder = project_dir / new_folder_name
    if new_folder.exists():
        print(f"{new_folder} already exists")  # noqa: T201
        return
    if not old_folder.exists():
        print(f"{old_folder} doesnt exist")  # noqa: T201
        return
    if get_confirmation(
        f"[{old_folder.name}] found in dir. Rename to [{new_folder.name}]?",
        default_option=True,
    ):
        old_folder.rename(new_folder)


def rename_systemd_unit(
    *,
    project_dir: pathlib.Path,
    old_app_name: str,
    new_app_name: str,
) -> None:
    old_systemd_unit = project_dir / "infra" / "systemd" / f"{old_app_name}.service"
    new_systemd_unit = project_dir / "infra" / "systemd" / f"{new_app_name}.service"
    if new_systemd_unit.exists():
        print(f"{new_systemd_unit} already exists")  # noqa: T201
        return
    if not old_systemd_unit.exists():
        print(f"{old_systemd_unit} doesnt exist")  # noqa: T201
        return
    if get_confirmation(
        f"[{old_systemd_unit.name}] found in infra/systemd. Rename to [{new_systemd_unit.name}]?",
        default_option=True,
    ):
        old_systemd_unit.rename(new_systemd_unit)




def rename_infra_files(
    *,
    project_dir: pathlib.Path,
    old_app_name: str,
    new_app_name: str,
) -> None:
    rename_systemd_unit(
        project_dir=project_dir,
        old_app_name=old_app_name,
        new_app_name=new_app_name,
    )


def rename_app_in_py_normal(
    *,
    project_dir: pathlib.Path,
    old_app_name: str,
    new_app_name: str,
) -> None:
    if get_confirmation(
        f"replace all [{old_app_name}] with [{new_app_name}] in .py files?",
        default_option=True,
    ):
        subprocess.call(
            [  # noqa: S603, S607
                "find",
                project_dir / new_app_name,
                "-type",
                "f",
                "-name",
                "*.py",
                "-exec",
                "sed",
                "-i",
                f"s/{old_app_name}/{new_app_name}/g",
                "{}",
                ";",
            ],
        )


def rename_app_in_py_capitalized(
    *,
    project_dir: pathlib.Path,
    old_app_name: str,
    new_app_name: str,
) -> None:
    capitilized_old_app_name = "".join(capitalize_app_name(old_app_name))
    capitilized_new_app_name = "".join(capitalize_app_name(new_app_name))
    if get_confirmation(
        f"replace all [{capitilized_old_app_name}] with [{capitilized_new_app_name}] in .py files?",
        default_option=True,
    ):
        subprocess.call(
            [  # noqa: S603, S607
                "find",
                project_dir / new_app_name,
                "-type",
                "f",
                "-name",
                "*.py",
                "-exec",
                "sed",
                "-i",
                f"s/{capitilized_old_app_name}/{capitilized_new_app_name}/g",
                "{}",
                ";",
            ],
        )


def rename_app_in_py_capitalized_split_words(
    *,
    project_dir: pathlib.Path,
    old_app_name: str,
    new_app_name: str,
) -> None:
    capitilized_old_app_name_split_words = " ".join(capitalize_app_name(old_app_name))
    capitilized_new_app_name_split_words = " ".join(capitalize_app_name(new_app_name))
    if get_confirmation(
        f"replace all [{capitilized_old_app_name_split_words}] with [{capitilized_new_app_name_split_words}] in .py files?",
        default_option=True,
    ):
        subprocess.call(
            [  # noqa: S603, S607
                "find",
                project_dir / new_app_name,
                "-type",
                "f",
                "-name",
                "*.py",
                "-exec",
                "sed",
                "-i",
                f"s/{capitilized_old_app_name_split_words}/{capitilized_new_app_name_split_words}/Ig",
                "{}",
                ";",
            ],
        )


def rename_app_in_py(
    *,
    project_dir: pathlib.Path,
    old_app_name: str,
    new_app_name: str,
) -> None:
    rename_app_in_py_normal(
        project_dir=project_dir,
        old_app_name=old_app_name,
        new_app_name=new_app_name,
    )
    rename_app_in_py_capitalized(
        project_dir=project_dir,
        old_app_name=old_app_name,
        new_app_name=new_app_name,
    )
    rename_app_in_py_capitalized_split_words(
        project_dir=project_dir,
        old_app_name=old_app_name,
        new_app_name=new_app_name,
    )


def rename_app_in_project_toml(
    *,
    project_dir: pathlib.Path,
    old_app_name: str,
    new_app_name: str,
) -> None:
    def get_new_line(
        *,
        current_line: str,
        replacements_list: list[tuple[str, str]],
    ) -> str:
        for old_line, replacement in replacements_list:
            if current_line.startswith(old_line):
                return replacement
        if current_line.startswith(
            'description = "Template for creating scalable bots with aiogram"',
        ) and get_confirmation(
            "Change project description in pyproject.toml?",
            default_option=True,
        ):
            new_description = input(
                "Input new description (old: [Template for creating scalable bots with aiogram]): ",
            )
            return f'description = "{new_description}"\n'
        return current_line

    replacements = [
        (
            f'name = "{DEFAULT_PROJECT_DIR}"',
            f'name = "{PROJECT_DIR_NAME}"\n',
        ),
        (
            f'packages = [{{ include = "{old_app_name}" }}]',
            f'packages = [{{ include = "{new_app_name}" }}]\n',
        ),
        (
            f'{old_app_name} = "{old_app_name}.bot:main"',
            f'{new_app_name} = "{new_app_name}.bot:main"\n',
        ),
    ]
    pyproject_file = project_dir / "pyproject.toml"
    with pyproject_file.open(mode="r") as f:
        data = f.readlines()
    new_data = [
        get_new_line(current_line=line, replacements_list=replacements) for line in data
    ]
    with pyproject_file.open(mode="w") as f:
        f.writelines(new_data)


def rename_app_in_cicd(
    *,
    project_dir: pathlib.Path,
    old_app_name: str,
    new_app_name: str,
) -> None:
    if get_confirmation(
        f"replace all [{old_app_name}] with [{new_app_name}] in ./github/workflows/.yml files?",
        default_option=True,
    ):
        subprocess.call(
            [  # noqa: S603, S607
                "find",
                project_dir / ".github" / "workflows",
                "-type",
                "f",
                "-name",
                "*.yml",
                "-exec",
                "sed",
                "-i",
                f"s/{old_app_name}/{new_app_name}/g",
                "{}",
                ";",
            ],
        )


def rename_app_in_makefile(
    *,
    project_dir: pathlib.Path,
    old_app_name: str,
    new_app_name: str,
) -> None:
    if get_confirmation(
        f"replace all [{old_app_name}] with [{new_app_name}] in Makefile?",
        default_option=True,
    ):
        subprocess.call(
            [  # noqa: S603, S607
                "find",
                project_dir,
                "-type",
                "f",
                "-name",
                "Makefile",
                "-exec",
                "sed",
                "-i",
                f"s/{old_app_name}/{new_app_name}/g",
                "{}",
                ";",
            ],
        )


def init_project() -> None:
    app_name = get_app_name(PROJECT_DIR_NAME)
    print(f"{app_name=}")  # noqa: T201
    rename_app_folder(
        project_dir=PROJECT_DIR,
        old_folder_name=DEFAULT_APP_FOLDER_NAME,
        new_folder_name=app_name,
    )
    rename_infra_files(
        project_dir=PROJECT_DIR,
        old_app_name=DEFAULT_APP_FOLDER_NAME,
        new_app_name=app_name,
    )
    rename_app_in_py(
        project_dir=PROJECT_DIR,
        old_app_name=DEFAULT_APP_FOLDER_NAME,
        new_app_name=app_name,
    )
    rename_app_in_project_toml(
        project_dir=PROJECT_DIR,
        old_app_name=DEFAULT_APP_FOLDER_NAME,
        new_app_name=app_name,
    )
    rename_app_in_cicd(
        project_dir=PROJECT_DIR,
        old_app_name=DEFAULT_APP_FOLDER_NAME,
        new_app_name=app_name,
    )
    rename_app_in_makefile(
        project_dir=PROJECT_DIR,
        old_app_name=DEFAULT_APP_FOLDER_NAME,
        new_app_name=app_name,
    )


if __name__ == "__main__":
    init_project()
