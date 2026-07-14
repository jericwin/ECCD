using ECCD.Application.Common.Interfaces;
using Microsoft.Extensions.Logging;

namespace ECCD.Infrastructure.Services;

/// <summary>
/// Local file storage for development. Stores files under wwwroot/uploads.
/// Swap with S3/Cloudinary implementation in production.
/// </summary>
public class FileStorageService : IFileStorageService
{
    private readonly ILogger<FileStorageService> _logger;
    private const string UploadRoot = "wwwroot/uploads";

    public FileStorageService(ILogger<FileStorageService> logger)
    {
        _logger = logger;
    }

    public async Task<string> UploadAsync(Stream fileStream, string fileName, string folder, CancellationToken cancellationToken = default)
    {
        var folderPath = Path.Combine(UploadRoot, folder);
        Directory.CreateDirectory(folderPath);

        var uniqueName = $"{Guid.NewGuid()}_{fileName}";
        var filePath = Path.Combine(folderPath, uniqueName);

        using var output = File.Create(filePath);
        await fileStream.CopyToAsync(output, cancellationToken);

        _logger.LogInformation("File uploaded: {FilePath}", filePath);
        return $"/uploads/{folder}/{uniqueName}";
    }

    public Task<Stream?> DownloadAsync(string filePath, CancellationToken cancellationToken = default)
    {
        var fullPath = Path.Combine(UploadRoot, filePath.TrimStart('/').Replace("uploads/", ""));
        if (!File.Exists(fullPath))
            return Task.FromResult<Stream?>(null);

        Stream stream = File.OpenRead(fullPath);
        return Task.FromResult<Stream?>(stream);
    }

    public Task DeleteAsync(string filePath, CancellationToken cancellationToken = default)
    {
        var fullPath = Path.Combine(UploadRoot, filePath.TrimStart('/').Replace("uploads/", ""));
        if (File.Exists(fullPath))
        {
            File.Delete(fullPath);
            _logger.LogInformation("File deleted: {FilePath}", fullPath);
        }
        return Task.CompletedTask;
    }
}
