import requests
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

def map_reduce(input_data):
    """Функція для виконання MapReduce."""
    # Map фаза: розбиваємо текст на слова і створюємо пари (слово, 1)
    def map_phase(text):
        words = re.findall(r'\w+', text.lower())
        return [(word, 1) for word in words]

    # Shuffle фаза: групуємо однакові ключі (слова)
    def shuffle_phase(mapped_values):
        grouped_data = {}
        for pair in mapped_values:
            word, count = pair
            if word in grouped_data:
                grouped_data[word].append(count)
            else:
                grouped_data[word] = [count]
        return grouped_data

    # Reduce фаза: підраховуємо кількість кожного слова
    def reduce_phase(grouped_data):
        return {word: sum(counts) for word, counts in grouped_data.items()}

    # Виконання Map фази в множинних потоках
    with ThreadPoolExecutor() as executor:
        map_results = executor.map(map_phase, input_data)

    # Об'єднання результатів Map фази
    mapped_values = [pair for result in map_results for pair in result]

    # Shuffle і Reduce фази
    grouped_data = shuffle_phase(mapped_values)
    reduced_data = reduce_phase(grouped_data)

    return reduced_data

def visualize_top_words(word_counts, top_n=10):
    """Візуалізація топ-N слів за частотою."""
    # Відбираємо топ-N слів
    top_words = Counter(word_counts).most_common(top_n)
    words, counts = zip(*top_words)

    # Створюємо бар-графік
    plt.bar(words, counts)
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)
    plt.title('Top Words Frequency')
    plt.show()

def main():
    """Основна функція скрипта."""
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"  # URL до книги
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевіряємо на помилки HTTP
        text = response.text

        # Виконуємо MapReduce
        word_counts = map_reduce([text])

        # Візуалізуємо результати
        visualize_top_words(word_counts)

    except requests.RequestException as e:
        print(f'Error fetching data from URL: {e}')

if __name__ == '__main__':
    main()