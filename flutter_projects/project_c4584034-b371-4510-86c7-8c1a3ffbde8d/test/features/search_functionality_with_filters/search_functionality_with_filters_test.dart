```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import '../lib/services/search_service.dart';
import '../lib/models/search_filter.dart';
import '../lib/models/search_result.dart';
import '../lib/repositories/search_repository.dart';

// Generate mocks
@GenerateMocks([SearchRepository])
import 'search_functionality_test.mocks.dart';

void main() {
  late MockSearchRepository mockSearchRepository;
  late SearchService searchService;

  setUp(() {
    mockSearchRepository = MockSearchRepository();
    searchService = SearchService(repository: mockSearchRepository);
  });

  tearDown(() {
    reset(mockSearchRepository);
  });

  group('Search Functionality Tests -', () {
    
    group('Basic Search -', () {
      test('should return search results when query is valid', () async {
        // Arrange
        const query = 'test query';
        final expectedResults = [
          SearchResult(id: '1', title: 'Result 1'),
          SearchResult(id: '2', title: 'Result 2'),
        ];
        
        when(mockSearchRepository.search(query))
            .thenAnswer((_) async => expectedResults);

        // Act
        final results = await searchService.search(query);

        // Assert
        expect(results, equals(expectedResults));
        verify(mockSearchRepository.search(query)).called(1);
      });

      test('should return empty list when no results found', () async {
        // Arrange
        const query = 'nonexistent';
        when(mockSearchRepository.search(query))
            .thenAnswer((_) async => []);

        // Act
        final results = await searchService.search(query);

        // Assert
        expect(results, isEmpty);
        verify(mockSearchRepository.search(query)).called(1);
      });
    });

    group('Filtered Search -', () {
      test('should apply filters correctly', () async {
        // Arrange
        const query = 'test';
        final filters = SearchFilter(
          category: 'books',
          minPrice: 10.0,
          maxPrice: 50.0,
          sortBy: 'price'
        );
        
        final expectedResults = [
          SearchResult(
            id: '1', 
            title: 'Book 1',
            category: 'books',
            price: 15.0
          ),
        ];

        when(mockSearchRepository.searchWithFilters(query, filters))
            .thenAnswer((_) async => expectedResults);

        // Act
        final results = await searchService.searchWithFilters(query, filters);

        // Assert
        expect(results, equals(expectedResults));
        verify(mockSearchRepository.searchWithFilters(query, filters)).called(1);
      });

      test('should handle invalid filter combinations', () async {
        // Arrange
        const query = 'test';
        final invalidFilters = SearchFilter(
          minPrice: 50.0,
          maxPrice: 10.0 // Invalid: min > max
        );

        // Act & Assert
        expect(
          () => searchService.searchWithFilters(query, invalidFilters),
          throwsA(isA<InvalidFilterException>())
        );
      });
    });

    group('Error Handling -', () {
      test('should throw SearchException when repository fails', () async {
        // Arrange
        const query = 'test';
        when(mockSearchRepository.search(query))
            .thenThrow(SearchException('Search failed'));

        // Act & Assert
        expect(
          () => searchService.search(query),
          throwsA(isA<SearchException>())
        );
      });

      test('should handle network errors gracefully', () async {
        // Arrange
        const query = 'test';
        when(mockSearchRepository.search(query))
            .thenThrow(NetworkException('Network error'));

        // Act & Assert
        expect(
          () => searchService.search(query),
          throwsA(isA<NetworkException>())
        );
      });
    });

    group('Edge Cases -', () {
      test('should handle empty query string', () async {
        // Arrange
        const query = '';
        
        // Act & Assert
        expect(
          () => searchService.search(query),
          throwsA(isA<InvalidQueryException>())
        );
      });

      test('should handle very long query strings', () async {
        // Arrange
        final query = 'a' * 1000; // Very long string
        
        // Act & Assert
        expect(
          () => searchService.search(query),
          throwsA(isA<InvalidQueryException>())
        );
      });

      test('should handle special characters in query', () async {
        // Arrange
        const query = '!@#\$%^&*()';
        final expectedResults = <SearchResult>[];
        
        when(mockSearchRepository.search(query))
            .thenAnswer((_) async => expectedResults);

        // Act
        final results = await searchService.search(query);

        // Assert
        expect(results, isEmpty);
        verify(mockSearchRepository.search(query)).called(1);
      });
    });

    group('Pagination Tests -', () {
      test('should handle pagination correctly', () async {
        // Arrange
        const query = 'test';
        const page = 2;
        const pageSize = 10;
        
        final expectedResults = List.generate(
          pageSize,
          (i) => SearchResult(id: '$i', title: 'Result $i')
        );

        when(mockSearchRepository.searchPaginated(query, page, pageSize))
            .thenAnswer((_) async => expectedResults);

        // Act
        final results = await searchService.searchPaginated(
          query, 
          page, 
          pageSize
        );

        // Assert
        expect(results.length, equals(pageSize));
        verify(mockSearchRepository.searchPaginated(query, page, pageSize))
            .called(1);
      });

      test('should handle last page with fewer items', () async {
        // Arrange
        const query = 'test';
        const page = 5;
        const pageSize = 10;
        final lastPageItems = 3;
        
        final expectedResults = List.generate(
          lastPageItems,
          (i) => SearchResult(id: '$i', title: 'Result $i')
        );

        when(mockSearchRepository.searchPaginated(query, page, pageSize))
            .thenAnswer((_) async => expectedResults);

        // Act
        final results = await searchService.searchPaginated(
          query, 
          page, 
          pageSize
        );

        // Assert
        expect(results.length, equals(lastPageItems));
        verify(mockSearchRepository.searchPaginated(query, page, pageSize))
            .called(1);
      });
    });
  });
}
```