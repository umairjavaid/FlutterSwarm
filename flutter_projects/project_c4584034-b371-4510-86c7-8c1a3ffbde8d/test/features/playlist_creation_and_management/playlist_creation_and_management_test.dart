```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import '../lib/features/playlist/domain/playlist.dart';
import '../lib/features/playlist/domain/playlist_repository.dart';
import '../lib/features/playlist/application/playlist_service.dart';
import '../lib/core/errors/failures.dart';
import 'package:dartz/dartz.dart';

@GenerateMocks([PlaylistRepository])
void main() {
  late PlaylistService playlistService;
  late MockPlaylistRepository mockPlaylistRepository;

  setUp(() {
    mockPlaylistRepository = MockPlaylistRepository();
    playlistService = PlaylistService(repository: mockPlaylistRepository);
  });

  final testPlaylist = Playlist(
    id: '1',
    name: 'My Playlist',
    description: 'Test playlist',
    songs: [],
    createdAt: DateTime.now(),
  );

  group('createPlaylist', () {
    test(
      'should return Playlist when repository creates playlist successfully',
      () async {
        // arrange
        when(mockPlaylistRepository.createPlaylist(any))
            .thenAnswer((_) async => Right(testPlaylist));

        // act
        final result = await playlistService.createPlaylist(
          name: 'My Playlist',
          description: 'Test playlist',
        );

        // assert
        expect(result, Right(testPlaylist));
        verify(mockPlaylistRepository.createPlaylist(any));
        verifyNoMoreInteractions(mockPlaylistRepository);
      },
    );

    test(
      'should return Failure when repository fails to create playlist',
      () async {
        // arrange
        final failure = ServerFailure();
        when(mockPlaylistRepository.createPlaylist(any))
            .thenAnswer((_) async => Left(failure));

        // act
        final result = await playlistService.createPlaylist(
          name: 'My Playlist',
          description: 'Test playlist',
        );

        // assert
        expect(result, Left(failure));
        verify(mockPlaylistRepository.createPlaylist(any));
        verifyNoMoreInteractions(mockPlaylistRepository);
      },
    );

    test(
      'should return ValidationFailure when playlist name is empty',
      () async {
        // act
        final result = await playlistService.createPlaylist(
          name: '',
          description: 'Test playlist',
        );

        // assert
        expect(result, Left(ValidationFailure('Playlist name cannot be empty')));
        verifyZeroInteractions(mockPlaylistRepository);
      },
    );
  });

  group('updatePlaylist', () {
    test(
      'should return updated Playlist when repository updates successfully',
      () async {
        // arrange
        final updatedPlaylist = testPlaylist.copyWith(
          name: 'Updated Playlist',
          description: 'Updated description',
        );
        when(mockPlaylistRepository.updatePlaylist(any))
            .thenAnswer((_) async => Right(updatedPlaylist));

        // act
        final result = await playlistService.updatePlaylist(
          playlist: testPlaylist,
          name: 'Updated Playlist',
          description: 'Updated description',
        );

        // assert
        expect(result, Right(updatedPlaylist));
        verify(mockPlaylistRepository.updatePlaylist(any));
        verifyNoMoreInteractions(mockPlaylistRepository);
      },
    );

    test(
      'should return Failure when repository fails to update playlist',
      () async {
        // arrange
        final failure = ServerFailure();
        when(mockPlaylistRepository.updatePlaylist(any))
            .thenAnswer((_) async => Left(failure));

        // act
        final result = await playlistService.updatePlaylist(
          playlist: testPlaylist,
          name: 'Updated Playlist',
          description: 'Updated description',
        );

        // assert
        expect(result, Left(failure));
        verify(mockPlaylistRepository.updatePlaylist(any));
        verifyNoMoreInteractions(mockPlaylistRepository);
      },
    );
  });

  group('deletePlaylist', () {
    test(
      'should return success when repository deletes playlist successfully',
      () async {
        // arrange
        when(mockPlaylistRepository.deletePlaylist(any))
            .thenAnswer((_) async => const Right(unit));

        // act
        final result = await playlistService.deletePlaylist(testPlaylist);

        // assert
        expect(result, const Right(unit));
        verify(mockPlaylistRepository.deletePlaylist(testPlaylist.id));
        verifyNoMoreInteractions(mockPlaylistRepository);
      },
    );

    test(
      'should return Failure when repository fails to delete playlist',
      () async {
        // arrange
        final failure = ServerFailure();
        when(mockPlaylistRepository.deletePlaylist(any))
            .thenAnswer((_) async => Left(failure));

        // act
        final result = await playlistService.deletePlaylist(testPlaylist);

        // assert
        expect(result, Left(failure));
        verify(mockPlaylistRepository.deletePlaylist(testPlaylist.id));
        verifyNoMoreInteractions(mockPlaylistRepository);
      },
    );
  });

  group('addSongToPlaylist', () {
    final testSong = Song(
      id: '1',
      title: 'Test Song',
      artist: 'Test Artist',
    );

    test(
      'should return updated Playlist when song is added successfully',
      () async {
        // arrange
        final updatedPlaylist = testPlaylist.copyWith(
          songs: [...testPlaylist.songs, testSong],
        );
        when(mockPlaylistRepository.addSongToPlaylist(any, any))
            .thenAnswer((_) async => Right(updatedPlaylist));

        // act
        final result = await playlistService.addSongToPlaylist(
          playlist: testPlaylist,
          song: testSong,
        );

        // assert
        expect(result, Right(updatedPlaylist));
        verify(mockPlaylistRepository.addSongToPlaylist(
          testPlaylist.id,
          testSong.id,
        ));
        verifyNoMoreInteractions(mockPlaylistRepository);
      },
    );

    test(
      'should return Failure when adding duplicate song',
      () async {
        // arrange
        final playlistWithSong = testPlaylist.copyWith(
          songs: [testSong],
        );

        // act
        final result = await playlistService.addSongToPlaylist(
          playlist: playlistWithSong,
          song: testSong,
        );

        // assert
        expect(
          result,
          Left(ValidationFailure('Song already exists in playlist')),
        );
        verifyZeroInteractions(mockPlaylistRepository);
      },
    );
  });

  group('removeSongFromPlaylist', () {
    final testSong = Song(
      id: '1',
      title: 'Test Song',
      artist: 'Test Artist',
    );

    test(
      'should return updated Playlist when song is removed successfully',
      () async {
        // arrange
        final playlistWithSong = testPlaylist.copyWith(
          songs: [testSong],
        );
        final updatedPlaylist = testPlaylist.copyWith(
          songs: [],
        );
        when(mockPlaylistRepository.removeSongFromPlaylist(any, any))
            .thenAnswer((_) async => Right(updatedPlaylist));

        // act
        final result = await playlistService.removeSongFromPlaylist(
          playlist: playlistWithSong,
          song: testSong,
        );

        // assert
        expect(result, Right(updatedPlaylist));
        verify(mockPlaylistRepository.removeSongFromPlaylist(
          playlistWithSong.id,
          testSong.id,
        ));
        verifyNoMoreInteractions(mockPlaylistRepository);
      },
    );

    test(
      'should return Failure when song does not exist in playlist',
      () async {
        // act
        final result = await playlistService.removeSongFromPlaylist(
          playlist: testPlaylist,
          song: testSong,
        );

        // assert
        expect(
          result,
          Left(ValidationFailure('Song does not exist in playlist')),
        );
        verifyZeroInteractions(mockPlaylistRepository);
      },
    );
  });
}
```