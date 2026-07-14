using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Cdcs.Queries;

public record GetCdcsQuery : IRequest<Result<List<CdcDto>>>;

public class GetCdcsQueryHandler : IRequestHandler<GetCdcsQuery, Result<List<CdcDto>>>
{
    private readonly IApplicationDbContext _context;

    public GetCdcsQueryHandler(IApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Result<List<CdcDto>>> Handle(GetCdcsQuery request, CancellationToken cancellationToken)
    {
        var cdcs = await _context.ChildDevelopmentCenters
            .Select(c => new CdcDto
            {
                Id = c.Id,
                Name = c.Name,
                Address = c.Address
            })
            .ToListAsync(cancellationToken);

        return Result<List<CdcDto>>.Success(cdcs);
    }
}

public class CdcDto
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Address { get; set; } = string.Empty;
}
