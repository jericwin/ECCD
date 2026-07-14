using ECCD.Application.Common.Interfaces;
using ECCD.Domain.Common;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ECCD.Application.Parents.Queries;

public record GetParentsQuery : IRequest<Result<List<ParentDto>>>;

public class GetParentsQueryHandler : IRequestHandler<GetParentsQuery, Result<List<ParentDto>>>
{
    private readonly IApplicationDbContext _context;

    public GetParentsQueryHandler(IApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Result<List<ParentDto>>> Handle(GetParentsQuery request, CancellationToken cancellationToken)
    {
        var parents = await _context.ParentProfiles
            .Select(p => new ParentDto
            {
                Id = p.Id,
                FullName = p.FullName,
                RelationshipToLearner = p.RelationshipToLearner
            })
            .ToListAsync(cancellationToken);

        return Result<List<ParentDto>>.Success(parents);
    }
}

public class ParentDto
{
    public Guid Id { get; set; }
    public string FullName { get; set; } = string.Empty;
    public string RelationshipToLearner { get; set; } = string.Empty;
}
