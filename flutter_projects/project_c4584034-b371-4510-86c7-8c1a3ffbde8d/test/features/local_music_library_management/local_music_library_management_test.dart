```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:path_provider/path_provider.dart' as path_provider;
import '../lib/features/local_music_library_management/domain/repositories/local_music_repository.dart';
import '../lib/features/local_music_library_management/domain/entities/song.dart';
import '../lib/features/local_music_library_management/data/models/song_model.dart';
import '../lib/features/local_music_library_management/domain/usecases/get_local_songs.dart';
import '../lib/features/local_music_library_management/domain/usecases/add_song.dart';
import '../lib/features/local_music_library_management/domain/usecases/delete_song.dart';
import '../lib/core/error/failures.dart';
import 'package:dartz/dartz.dart';

@GenerateMocks([LocalMusicRepository, path_provider.PathProvider])
void main() {
  late MockLocalMusicRepository mockRepository;
  late GetLocalSongs getLocalSongs;
  late AddSong addSong;
  late DeleteSong deleteSong;
  late MockPathProvider mockPathProvider;

  setUp(() {
    mockRepository = MockLocalMusicRepository();
    mockPathProvider = MockPathProvider();
    getLocalSongs = GetLocalSongs(mockRepository);
    addSong = AddSong(mockRepository);
    deleteSong = DeleteSong(mockRepository);
  });

  final testSong = Song(
    id: '1',
    title: 'Test Song',
    artist: 'Test Artist',
    duration: const Duration(minutes: 3, seconds: 30),
    filePath: '/test/path/song.mp3',
  );

  final testSongModel = SongModel(
    id: '1',
    title: 'Test Song',
    artist: 'Test Artist', 
    duration: const Duration(minutes: 3, seconds: 30),
    filePath: '/test/path/song.mp3',
  );

  group('GetLocalSongs', () {
    test(
      'should return list of songs when repository call is successful',
      () async {
        // arrange
        when(mockRepository.getLocalSongs())
            .thenAnswer((_) async => Right([testSong]));

        // act
        final result = await getLocalSongs();

        // assert
        expect(result, Right([testSong]));
        verify(mockRepository.getLocalSongs());
        verifyNoMoreInteractions(mockRepository);
      },
    );

    test(
      'should return FileSystemFailure when repository call fails',
      () async {
        // arrange
        when(mockRepository.getLocalSongs())
            .thenAnswer((_) async => Left(FileSystemFailure()));

        // act
        final result = await getLocalSongs();

        // assert
        expect(result, Left(FileSystemFailure()));
        verify(mockRepository.getLocalSongs());
        verifyNoMoreInteractions(mockRepository);
      },
    );
  });

  group('AddSong', () {
    test(
      'should return success when song is added successfully',
      () async {
        // arrange
        when(mockRepository.addSong(any))
            .thenAnswer((_) async => Right(testSong));

        // act
        final result = await addSong(testSongModel);

        // assert
        expect(result, Right(testSong));
        verify(mockRepository.addSong(testSongModel));
        verifyNoMoreInteractions(mockRepository);
      },
    );

    test(
      'should return FileSystemFailure when adding song fails',
      () async {
        // arrange
        when(mockRepository.addSong(any))
            .thenAnswer((_) async => Left(FileSystemFailure()));

        // act
        final result = await addSong(testSongModel);

        // assert
        expect(result, Left(FileSystemFailure()));
        verify(mockRepository.addSong(testSongModel));
        verifyNoMoreInteractions(mockRepository);
      },
    );

    test(
      'should return ValidationFailure when song data is invalid',
      () async {
        // arrange
        final invalidSong = SongModel(
          id: '',
          title: '',
          artist: '',
          duration: const Duration(seconds: 0),
          filePath: '',
        );

        when(mockRepository.addSong(any))
            .thenAnswer((_) async => Left(ValidationFailure()));

        // act
        final result = await addSong(invalidSong);

        // assert
        expect(result, Left(ValidationFailure()));
        verify(mockRepository.addSong(invalidSong));
        verifyNoMoreInteractions(mockRepository);
      },
    );
  });

  group('DeleteSong', () {
    test(
      'should return success when song is deleted successfully',
      () async {
        // arrange
        when(mockRepository.deleteSong(any))
            .thenAnswer((_) async => const Right(unit));

        // act
        final result = await deleteSong(testSong.id);

        // assert
        expect(result, const Right(unit));
        verify(mockRepository.deleteSong(testSong.id));
        verifyNoMoreInteractions(mockRepository);
      },
    );

    test(
      'should return FileSystemFailure when deleting song fails',
      () async {
        // arrange
        when(mockRepository.deleteSong(any))
            .thenAnswer((_) async => Left(FileSystemFailure()));

        // act
        final result = await deleteSong(testSong.id);

        // assert
        expect(result, Left(FileSystemFailure()));
        verify(mockRepository.deleteSong(testSong.id));
        verifyNoMoreInteractions(mockRepository);
      },
    );

    test(
      'should return NotFoundFailure when song does not exist',
      () async {
        // arrange
        when(mockRepository.deleteSong(any))
            .thenAnswer((_) async => Left(NotFoundFailure()));

        // act
        final result = await deleteSong('non_existent_id');

        // assert
        expect(result, Left(NotFoundFailure()));
        verify(mockRepository.deleteSong('non_existent_id'));
        verifyNoMoreInteractions(mockRepository);
      },
    );
  });

  group('Edge Cases', () {
    test(
      'should handle empty song list correctly',
      () async {
        // arrange
        when(mockRepository.getLocalSongs())
            .thenAnswer((_) async => const Right([]));

        // act
        final result = await getLocalSongs();

        // assert
        expect(result, const Right([]));
        verify(mockRepository.getLocalSongs());
        verifyNoMoreInteractions(mockRepository);
      },
    );

    test(
      'should handle very large song titles',
      () async {
        // arrange
        final longTitleSong = SongModel(
          id: '1',
          title: 'A' * 1000, // Very long title
          artist: 'Test Artist',
          duration: const Duration(minutes: 3, seconds: 30),
          filePath: '/test/path/song.mp3',
        );

        when(mockRepository.addSong(any))
            .thenAnswer((_) async => Left(ValidationFailure()));

        // act
        final result = await addSong(longTitleSong);

        // assert
        expect(result, Left(ValidationFailure()));
        verify(mockRepository.addSong(longTitleSong));
        verifyNoMoreInteractions(mockRepository);
      },
    );

    test(
      'should handle special characters in file paths',
      () async {
        // arrange
        final specialPathSong = SongModel(
          id: '1',
          title: 'Test Song',
          artist: 'Test Artist',
          duration: const Duration(minutes: 3, seconds: 30),
          filePath: '/test/path/with spaces and #special @chars/song.mp3',
        );

        when(mockRepository.addSong(any))
            .thenAnswer((_) async => Right(testSong));

        // act
        final result = await addSong(specialPathSong);

        // assert
        expect(result, Right(testSong));
        verify(mockRepository.addSong(specialPathSong));
        verifyNoMoreInteractions(mockRepository);
      },
    );
  });
}
```