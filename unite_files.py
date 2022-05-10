import os
import fileinput, pathlib

def main():
    # каталог текстовых файлов
    # измените на свой
    pth = 'D:\\seafile\projects\\audit_AZ\\01_survey\\обследование_УАЗ\\Уральская фольга (Михайловск)\\Cisco\\247'
    # маска поиска файлов по расширению
    pattern = '*.txt'

    files_path = pathlib.Path(pth)
    list_files = files_path.glob(pattern)
    # общий файл, создадим в текущем каталоге
    new_file = 'D:\\seafile\projects\\audit_AZ\\01_survey\\обследование_УАЗ\\Уральская фольга (Михайловск)\\Cisco\\247\\all_config.cfg'

    if list_files:
        with fileinput.FileInput(files=list_files) as fr, open(new_file, 'w') as fw:
            for line in fr:
                # определяем первую строку
                # читаемого файла из каталога
                if fr.isfirstline():
                    # название читаемого файла
                    file_name = fr.filename()
                    # дописываем строку с названием файла
#                    fw.write(f'\n\n------------ {file_name}\n\n')
                # пишем данные
                fw.write(line)

if __name__ == '__main__':
    main()