import os


def main():
    os.makedirs('test_reports', exist_ok=True)
    with open(os.path.join('test_reports', 'validate_output.txt'), 'w', encoding='utf-8') as f:
        f.write('Lune removido. Validador desativado.\n')


if __name__ == '__main__':
    main()
